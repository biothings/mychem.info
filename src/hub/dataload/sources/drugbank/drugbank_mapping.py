drugbank_mapping = {
    "drugbank": {
        "properties": {
            "id": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword",
                "copy_to": ["all"]
            },
            "accession_number": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword",
                "copy_to": ["all"]
            },
            "name": {
                "type": "text",
                "copy_to": ["all"]
            },
            "cas_rn": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer",
                "copy_to": ["all"]
            },
            "unii": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "synonyms": {
                "type": "text",
            },
            "inchikey": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            }
        }
    }
}
