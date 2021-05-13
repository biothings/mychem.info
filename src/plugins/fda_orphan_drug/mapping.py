def get_customized_mapping(cls):
    mapping = {
          "fda_orphan_drug": {
                "properties": {
                    "designated_date": {
                    "type": "date"
                },
                "designation_status": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "orphan_designation": {
                  "properties": {
                    "original_text": {
                        "type": "text",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "umls": {
                        "type": "text",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "parsed_text": {
                        "type": "text",
                        "copy_to": [
                            "all"
                        ]
                    }
                  }
                },
                "marketing_approval_date": {
                  "type": "date"
                },
                "exclusivity_end_date": {
                  "type": "date"
                },
                "pubchem_cid": {
                  "type": "integer",
                  "copy_to": [
                    "all"
                  ]
                },
                "inchikey": {
                  "normalizer": "keyword_lowercase_normalizer",
                  "type": "keyword"
                },
                "trade_name": {
                  "type": "text"
                },
                "approved_labeled_indication": {
                  "type": "text"
                },
                "exclusivity_protected_indication": {
                  "type": "text"
                },
                "pubchem_sid": {
                  "type": "text"
                },
                "generic_name": {
                  "type": "text",
                  "copy_to": [
                    "all"
                  ]
                },
                "approval_status": {
                  "type": "text"
                },
                "sponsor": {
                  "type": "text",
                  "index": "false"
                }
            }
        }
        
      }
    return mapping
