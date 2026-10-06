import functools
import gzip
import re

from biothings.utils.dataload import value_convert_to_number

# A PubChem Compound XML record is ~40KB, mostly atom, bond and 2D coordinate
# elements we don't use, and building ElementTree elements for all of them made
# parsing ~10x slower. Records are instead split on their closing tag and only the
# few sections we need (id, charge, props, count) are matched on the raw bytes.

CHUNK_SIZE = 256 * 1024  # bigger isn't faster, only uses more memory
RECORD_END = b"</PC-Compound>"
ROOT_END = b"</PC-Compounds>"

CID_RE = re.compile(rb"<PC-CompoundType_id_cid>([^<]*)</PC-CompoundType_id_cid>")
CHARGE_RE = re.compile(rb"<PC-Compound_charge>([^<]*)</PC-Compound_charge>")
LABEL_RE = re.compile(rb"<PC-Urn_label>([^<]*)</PC-Urn_label>")
NAME_RE = re.compile(rb"<PC-Urn_name>([^<]*)</PC-Urn_name>")
VALUE_RE = re.compile(rb"<PC-InfoData_value_(sval|ival|fval)>([^<]*)</PC-InfoData_value_\1>")
COUNT_RE = re.compile(rb"<PC-Count_([a-z-]+)>([^<]*)</PC-Count_\1>")
ENTITY_RE = re.compile(r"&(#x[0-9a-fA-F]+|#[0-9]+|lt|gt|amp|apos|quot);")
XML_ENTITIES = {"lt": "<", "gt": ">", "amp": "&", "apos": "'", "quot": '"'}

# PC-Urn_label -> (field, value types it is read from)
LABEL_FIELDS = {
    "InChI": ("inchi", ("sval",)),
    "InChIKey": ("inchikey", ("sval",)),
    "Log P": ("xlogp", ("fval",)),
    "Mass": ("exact_mass", ("sval", "fval")),
    "Molecular Formula": ("molecular_formula", ("sval",)),
    "Molecular Weight": ("molecular_weight", ("sval", "fval")),
    "Topological": ("topological_polar_surface_area", ("fval",)),
    "Weight": ("monoisotopic_weight", ("sval", "fval")),
    "Compound Complexity": ("complexity", ("fval",)),
}
# PC-Urn_name -> (field, value types it is read from), whatever the label
NAME_FIELDS = {
    "Hydrogen Bond Acceptor": ("hydrogen_bond_acceptor_count", ("ival",)),
    "Hydrogen Bond Donor": ("hydrogen_bond_donor_count", ("ival",)),
    "Rotatable Bond": ("rotatable_bond_count", ("ival",)),
}
# labels whose values are keyed by their PC-Urn_name, eg. iupac.cas_like_style
NAMED_LABELS = {"IUPAC Name": "iupac", "SMILES": "smiles"}
# PC-Count_<suffix> -> field
COUNT_FIELDS = {
    "heavy-atom": "heavy_atom_count",
    "atom-chiral": "chiral_atom_count",
    "bond-chiral": "chiral_bond_count",
    "atom-chiral-def": "defined_chiral_atom_count",
    "bond-chiral-def": "defined_chiral_bond_count",
    "atom-chiral-undef": "undefined_chiral_atom_count",
    "bond-chiral-undef": "undefined_chiral_bond_count",
    "isotope-atom": "isotope_atom_count",
    "covalent-unit": "covalent_unit_count",
    "tautomers": "tautomers_count",
}


def load_annotations(input_file):
    """Main function to load data from individual xml files"""
    for record in iter_records(input_file):
        yield parse_record(record, input_file)


def iter_records(input_file):
    """Yield the raw bytes of each PC-Compound element of a gzipped XML file"""
    with gzip.open(input_file, "rb") as f:
        buf = b""
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            buf += chunk
            start = 0
            end = buf.find(RECORD_END)
            while end >= 0:
                end += len(RECORD_END)
                yield buf[start:end]
                start = end
                end = buf.find(RECORD_END, start)
            buf = buf[start:]
    # a truncated file would otherwise just yield fewer compounds
    if not buf.rstrip().endswith(ROOT_END):
        raise ValueError("File {} doesn't end with {}, it may be truncated".format(input_file, ROOT_END.decode()))


def unescape_entity(match):
    entity = match.group(1)
    if entity.startswith("#x"):
        return chr(int(entity[2:], 16))
    if entity.startswith("#"):
        return chr(int(entity[1:]))
    return XML_ENTITIES[entity]


def text(value):
    """Decode an element's raw text, unescaping XML entities (eg. &lt;I&gt; in IUPAC markup names)"""
    value = value.decode("utf-8")
    return ENTITY_RE.sub(unescape_entity, value) if "&" in value else value


def section(record, tag):
    """Raw bytes of the first <tag> element of a record, or b"" if absent"""
    start = record.find(b"<" + tag + b">")
    if start < 0:
        return b""
    return record[start:record.find(b"</" + tag + b">", start)]


def parse_record(record, input_file):
    """Build the document of a PC-Compound record"""
    current_compound = {}
    cid = CID_RE.search(record)
    assert cid and cid.group(1), "File {} has document missing CID. Every document must have a CID.".format(input_file)
    compound_data = {"cid": text(cid.group(1)), "iupac": {}, "smiles": {}}

    charge = CHARGE_RE.search(record)
    if charge and charge.group(1):
        compound_data["formal_charge"] = text(charge.group(1))

    for info in section(record, b"PC-Compound_props").split(b"</PC-InfoData>"):
        value = VALUE_RE.search(info)
        if not value:
            continue
        value_type, value = value.group(1).decode(), value.group(2)
        label = LABEL_RE.search(info)
        label = text(label.group(1)) if label else None
        name = NAME_RE.search(info)
        name = text(name.group(1)) if name else None
        if name in NAME_FIELDS:
            field, value_types = NAME_FIELDS[name]
        elif label in NAMED_LABELS:
            if name and value and value_type == "sval":
                compound_data[NAMED_LABELS[label]][camel_to_snake(name)] = text(value)
            continue
        elif label in LABEL_FIELDS:
            field, value_types = LABEL_FIELDS[label]
        else:
            continue
        if value and value_type in value_types:
            if field == "inchikey":
                current_compound["_id"] = text(value)
            compound_data[field] = text(value)

    for suffix, value in COUNT_RE.findall(section(record, b"PC-Compound_count")):
        field = COUNT_FIELDS.get(suffix.decode())
        if field and value:
            compound_data[field] = text(value)

    current_compound["pubchem"] = compound_data
    # Fall back to using cid if inchikey is not present
    if current_compound.get("_id") is None:
        current_compound["_id"] = compound_data["cid"]
    # Convert numeric values to float or integer
    return value_convert_to_number(current_compound, skipped_keys=["_id", "pubchem.cid"])


@functools.lru_cache(maxsize=None)
def camel_to_snake(s):
    """Convert camelCase strings to snake_case, keeping abbreviations together,
    and removing white space, and dashes."""
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
    s = s.replace("-", "_").replace(" _", "_").replace(" ", "_")
    return s


if __name__ == "__main__":
    import json
    import sys

    annotations = load_annotations(sys.argv[1])
    for a in annotations:
        print(json.dumps(a, indent=2))
