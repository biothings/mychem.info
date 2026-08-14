# FDA Orphan Drug source

This source downloads the complete Excel export directly from the
[FDA Orphan Drug Designations and Approvals database](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/).

The original [project report](https://github.com/r76941156/fda_orphan_drug/blob/main/FDA_orphan_drug_demo.pdf)
documents the enrichment process. FDA rows without a PubChem compound,
substance, or other MyChem identifier are intentionally excluded. The bundled
`reference.json.gz` snapshot was recovered from `mychem_src.fda_orphan_drug` on
2026-08-14 (3,661 documents containing 7,515 records). It preserves the prior
PubChem and UMLS enrichment for subsequent FDA exports.
