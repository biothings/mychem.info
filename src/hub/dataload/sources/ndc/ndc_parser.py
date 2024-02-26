import csv, os, re
from biothings.utils.dataload import dict_sweep, unlist

def parse_pharm_classes(pharm_classes_str):
    # Split on commas that are followed by a closing bracket for cases like: Anti-Inflammatory Agents, Non-Steroidal [CS]
    classes_list = [cls.strip() for cls in re.split(r"(?<=\]),\s*", pharm_classes_str)]
    return list(set(classes_list))

def package_restr_dict(dictionary):
    _d = {}
    _d['ndc'] = {}
    _d['ndc']['package'] = {}

    for key in dictionary:
        if key is None:
            continue
        if key == 'PRODUCTID':
            _d.update({'_id':dictionary[key]})
            _d['ndc'].update({'product_id':dictionary[key]})
        elif key == 'NDCPACKAGECODE':
            _d['ndc']['package'].update({key.lower():dictionary[key]})
        elif key == 'PACKAGEDESCRIPTION':
            _d['ndc']['package'].update({key.lower():dictionary[key]})
        else:
            _d['ndc'].update({key.lower():dictionary[key]})
    return _d

def product_restr_dict(dictionary):
    _d = {}
    _d['ndc'] = {}
    for key in dictionary:
        if key is None:
            continue
        if key == 'PRODUCTID':
            _d.update({'_id':dictionary[key]})
            _d['ndc'].update({'product_id':dictionary[key]})
        elif key == "PHARM_CLASSES":
            pharm_classes_list = parse_pharm_classes(dictionary[key])
            _d["ndc"].update({"pharm_classes": pharm_classes_list})
        else:
            _d['ndc'].update({key.lower():dictionary[key]})
    return _d

def convert_to_unicode(dictionary):
    for key, val in dictionary.items():
        if isinstance(val, str):
            dictionary[key] = str(val)
        elif isinstance(val, dict):
            convert_to_unicode(val)
    return dictionary

def load_products(_file):
    f = open(_file,'r',encoding="latin1")
    reader = csv.DictReader(f,dialect='excel-tab')
    for row in reader:
        _dict = product_restr_dict(row)
        _dict = convert_to_unicode(dict_sweep(_dict))
        _dict["_id"] = _dict["ndc"]["productndc"]
        yield _dict

def load_packages(_file):
    f = open(_file,'r',encoding='latin1')
    reader = csv.DictReader(f,dialect='excel-tab')
    for row in reader:
        _dict = package_restr_dict(row)
        _dict = unlist(dict_sweep(_dict))
        _dict["_id"] = _dict["ndc"]["productndc"]
        yield _dict

def load_data(data_folder):
    package_file = os.path.join(data_folder,"package.txt")
    product_file = os.path.join(data_folder,"product.txt")
    assert os.path.exists(package_file), "Package file doesn't exist..."
    assert os.path.exists(product_file), "Product file doesn't exist..."
    package_ndc = {}
    inchi_key = {}
    for doc in load_packages(package_file):
        package_ndc.setdefault(doc["_id"],[]).append(doc["ndc"])
    for doc in load_products(product_file):
        packages = package_ndc.get(doc["_id"],[])
        if packages:
            doc["ndc"]["package"] = []
            for pack in packages:
                # remove keys used for the merge (duplicates, already in product
                pack.pop("product_id",None)
                pack.pop("productndc",None)
                doc["ndc"]["package"].append(pack)
            if len(doc["ndc"]["package"]) == 1:
                doc["ndc"]["package"] = doc["ndc"]["package"].pop() # to dict
        yield doc
