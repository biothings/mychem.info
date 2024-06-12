drugbank_open_mapping = {
    "drugbank": {
        "properties": {
            "id": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword",
                "copy_to": ["all"]
            },
            "accession_number": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "copy_to": ["name"]
            },
            "cas_number": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "unii": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "synonyms": {
                "type": "text"
            },
            "inchi_key": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            }
        }
    }
}
