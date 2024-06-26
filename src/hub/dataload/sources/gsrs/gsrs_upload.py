"""
GSRS Biothings Uploader
"""

# pylint: disable=E0401, E0611
import os

import biothings.hub.dataload.storage as storage

from hub.dataload.uploader import BaseDrugUploader

from .gsrs_parser import load_substances

SRC_META = {
    "url": "https://gsrs.ncats.nih.gov/",
    "license_url": "https://gsrs.ncats.nih.gov/#!/faqs#%2Frelease",
}


class GSRSUploader(BaseDrugUploader):
    """
    GSRS Uploader Class
    """

    name = "gsrs"
    __metadata__ = {"src_meta": SRC_META}

    def load_data(self, data_folder):
        """load_data method"""
        self.logger.info("Load data from '%s'" % data_folder)
        input_file = os.path.join(data_folder, "dump-public-2023-12-14.gsrs")
        assert os.path.exists(input_file), "Can't find input file '%s'" % input_file
        return load_substances(input_file)

    @classmethod
    def get_mapping(cls):
        """get mapping information"""
        mapping = {
            "gsrs": {
                "properties": {
                    "properties": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "propertyType": {"type": "text"},
                            "value": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "average": {"type": "float"},
                                    "high": {"type": "float"},
                                    "low": {"type": "float"},
                                    "highLimit": {"type": "float"},
                                    "lowLimit": {"type": "float"},
                                    "type": {"type": "text"},
                                    "units": {"type": "text"},
                                    "nonNumericValue": {"type": "text"},
                                }
                            },
                            "defining": {"type": "boolean"},
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "parameters": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "type": {"type": "text"},
                                    "value": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "high": {"type": "float"},
                                            "low": {"type": "float"},
                                            "average": {"type": "float"},
                                            "units": {"type": "text"},
                                            "type": {"type": "text"},
                                            "lowLimit": {"type": "float"},
                                            "nonNumericValue": {"type": "text"},
                                        }
                                    },
                                    "name": {"type": "text"},
                                }
                            },
                            "referencedSubstance": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "name": {"type": "text"},
                                }
                            },
                            "name": {"type": "text"},
                        }
                    },
                    "definitiontype": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "definitionlevel": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "substanceclass": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "status": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "version": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "approvedby": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "names": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "type": {"type": "text"},
                            "languages": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "preferred": {"type": "boolean"},
                            "displayName": {"type": "boolean"},
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "domains": {"type": "text"},
                            "nameOrgs": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "nameOrg": {"type": "text"},
                                    "deprecatedDate": {"type": "date"},
                                }
                            },
                            "nameJurisdiction": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "name": {"type": "text"},
                            "stdName": {"type": "text"},
                        }
                    },
                    "codes": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "url": {"type": "text"},
                            "codeText": {"type": "text"},
                            "type": {"type": "text"},
                            "code": {"type": "text"},
                            "comments": {"type": "text"},
                            "codeSystem": {"type": "text"},
                            "deprecated": {"type": "boolean"},
                        }
                    },
                    "modifications": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "physicalModifications": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "parameters": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "amount": {
                                                "properties": {
                                                    "uuid": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword",
                                                    },
                                                    "lowLimit": {"type": "float"},
                                                    "units": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword",
                                                    },
                                                    "nonNumericValue": {"type": "text"},
                                                    "highLimit": {"type": "float"},
                                                    "type": {"type": "text"},
                                                    "average": {"type": "float"},
                                                    "high": {"type": "float"},
                                                    "low": {"type": "float"},
                                                }
                                            },
                                            "parameterName": {"type": "text"},
                                        }
                                    },
                                    "physicalModificationRole": {"type": "text"},
                                }
                            },
                            "agentModifications": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "agentSubstance": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "name": {"type": "text"},
                                        }
                                    },
                                    "amount": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "nonNumericValue": {"type": "text"},
                                            "type": {"type": "text"},
                                            "average": {"type": "float"},
                                            "highLimit": {"type": "float"},
                                            "lowLimit": {"type": "float"},
                                            "units": {"type": "text"},
                                            "high": {"type": "float"},
                                            "low": {"type": "float"},
                                        }
                                    },
                                    "agentModificationRole": {"type": "text"},
                                    "agentModificationProcess": {"type": "text"},
                                    "agentModificationType": {"type": "text"},
                                }
                            },
                            "structuralModifications": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "molecularFragment": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "name": {"type": "text"},
                                        }
                                    },
                                    "sites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "extentAmount": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "type": {"type": "text"},
                                            "average": {"type": "float"},
                                            "units": {"type": "text"},
                                            "nonNumericValue": {"type": "text"},
                                            "high": {"type": "float"},
                                            "low": {"type": "float"},
                                            "highLimit": {"type": "float"},
                                            "lowLimit": {"type": "float"},
                                        }
                                    },
                                    "residueModified": {"type": "text"},
                                    "extent": {"type": "text"},
                                    "locationType": {"type": "text"},
                                    "structuralModificationType": {"type": "text"},
                                }
                            },
                        }
                    },
                    "relationships": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "relatedSubstance": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "name": {"type": "text"},
                                }
                            },
                            "originatorUuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "amount": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "lowLimit": {"type": "float"},
                                    "average": {"type": "float"},
                                    "highLimit": {"type": "float"},
                                    "low": {"type": "float"},
                                    "high": {"type": "float"},
                                    "units": {"type": "text"},
                                    "type": {"type": "text"},
                                    "nonNumericValue": {"type": "text"},
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "mediatorSubstance": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "name": {"type": "text"},
                                }
                            },
                            "comments": {"type": "text"},
                            "qualification": {"type": "text"},
                            "interactionType": {"type": "text"},
                            "type": {"type": "text"},
                        }
                    },
                    "references": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "publicDomain": {"type": "boolean"},
                            "tags": {"type": "text"},
                            "documentDate": {"type": "date"},
                            "uploadedFile": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "id": {"type": "text"},
                            "url": {"type": "text"},
                            "citation": {"type": "text"},
                            "docType": {"type": "text"},
                        }
                    },
                    "approvalid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "structurallydiverse": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "part": {"type": "text"},
                            "parentSubstance": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "name": {"type": "text"},
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "hybridSpeciesPaternalOrganism": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "name": {"type": "text"},
                                }
                            },
                            "hybridSpeciesMaternalOrganism": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "name": {"type": "text"},
                                }
                            },
                            "developmentalStage": {"type": "text"},
                            "organismFamily": {"type": "text"},
                            "fractionMaterialType": {"type": "text"},
                            "partLocation": {"type": "text"},
                            "sourceMaterialClass": {"type": "text"},
                            "sourceMaterialType": {"type": "text"},
                            "fractionName": {"type": "text"},
                            "organismGenus": {"type": "text"},
                            "organismSpecies": {"type": "text"},
                            "organismAuthor": {"type": "text"},
                            "sourceMaterialState": {"type": "text"},
                            "infraSpecificType": {"type": "text"},
                            "infraSpecificName": {"type": "text"},
                        }
                    },
                    "protein": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "glycosylation": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "glycosylationType": {"type": "text"},
                                    "NGlycosylationSites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "OGlycosylationSites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "CGlycosylationSites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                }
                            },
                            "subunits": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sequence": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "subunitIndex": {"type": "integer"},
                                    "length": {"type": "float"},
                                }
                            },
                            "disulfideLinks": {
                                "properties": {
                                    "sites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "sitesShorthand": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "otherLinks": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "linkageType": {"type": "text"},
                                }
                            },
                            "sequenceType": {"type": "text"},
                            "proteinType": {"type": "text"},
                            "sequenceOrigin": {"type": "text"},
                            "proteinSubType": {"type": "text"},
                        }
                    },
                    "structure": {
                        "properties": {
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "digest": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "smiles": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "formula": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "atropisomerism": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "stereoCenters": {"type": "integer"},
                            "definedStereo": {"type": "integer"},
                            "ezCenters": {"type": "integer"},
                            "charge": {"type": "integer"},
                            "mwt": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "count": {"type": "float"},
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "hash": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "stereochemistry": {"type": "text"},
                            "molfile": {"type": "text"},
                            "opticalActivity": {"type": "text"},
                            "stereoComments": {"type": "text"},
                        }
                    },
                    "moieties": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "digest": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "smiles": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "formula": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "atropisomerism": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "stereoCenters": {"type": "integer"},
                            "definedStereo": {"type": "integer"},
                            "ezCenters": {"type": "integer"},
                            "charge": {"type": "integer"},
                            "mwt": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "count": {"type": "integer"},
                            "stereochemistry": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "hash": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "countAmount": {
                                "properties": {
                                    "average": {"type": "float"},
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "lowLimit": {"type": "float"},
                                    "highLimit": {"type": "float"},
                                    "high": {"type": "float"},
                                    "low": {"type": "float"},
                                    "nonNumericValue": {"type": "text"},
                                    "type": {"type": "text"},
                                    "units": {"type": "text"},
                                }
                            },
                            "stereoComments": {"type": "text"},
                            "opticalActivity": {"type": "text"},
                            "molfile": {"type": "text"},
                        }
                    },
                    "mixture": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "components": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substance": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "name": {"type": "text"},
                                        }
                                    },
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "parentSubstance": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "refPname": {"type": "text"},
                                    "refuuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substanceClass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "approvalID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkingID": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "name": {"type": "text"},
                                }
                            },
                        }
                    },
                    "notes": {
                        "properties": {
                            "note": {"type": "text"},
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                        }
                    },
                    "polymer": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "classification": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "polymerClass": {"type": "text"},
                                    "polymerGeometry": {"type": "text"},
                                    "polymerSubclass": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sourceType": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "parentSubstance": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "name": {"type": "text"},
                                        }
                                    },
                                }
                            },
                            "displayStructure": {
                                "properties": {
                                    "id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "digest": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "molfile": {"type": "text"},
                                    "smiles": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "formula": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "opticalActivity": {"type": "text"},
                                    "atropisomerism": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "stereoCenters": {"type": "float"},
                                    "definedStereo": {"type": "float"},
                                    "ezCenters": {"type": "float"},
                                    "charge": {"type": "float"},
                                    "mwt": {"type": "float"},
                                    "count": {"type": "float"},
                                    "hash": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "stereochemistry": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                }
                            },
                            "idealizedStructure": {
                                "properties": {
                                    "id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "digest": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "molfile": {"type": "text"},
                                    "smiles": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "formula": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "opticalActivity": {"type": "text"},
                                    "atropisomerism": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "stereoCenters": {"type": "float"},
                                    "definedStereo": {"type": "float"},
                                    "ezCenters": {"type": "float"},
                                    "charge": {"type": "float"},
                                    "mwt": {"type": "float"},
                                    "count": {"type": "float"},
                                    "hash": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "stereochemistry": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                }
                            },
                            "monomers": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "amount": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "type": {"type": "text"},
                                            "average": {"type": "float"},
                                            "units": {"type": "text"},
                                            "highLimit": {"type": "float"},
                                            "lowLimit": {"type": "float"},
                                            "high": {"type": "float"},
                                            "low": {"type": "float"},
                                            "nonNumericValue": {"type": "text"},
                                        }
                                    },
                                    "monomerSubstance": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "name": {"type": "text"},
                                        }
                                    },
                                    "defining": {"type": "boolean"},
                                    "type": {"type": "text"},
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                        }
                    },
                    "nucleicacid": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "linkages": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "sitesShorthand": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "linkage": {"type": "text"},
                                }
                            },
                            "subunits": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sequence": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "subunitIndex": {"type": "integer"},
                                    "length": {"type": "float"},
                                }
                            },
                            "sugars": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sugar": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "sites": {
                                        "properties": {
                                            "subunitIndex": {"type": "integer"},
                                            "residueIndex": {"type": "integer"},
                                        }
                                    },
                                    "sitesShorthand": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "nucleicAcidSubType": {"type": "text"},
                            "sequenceOrigin": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "sequenceType": {"type": "text"},
                            "nucleicAcidType": {"type": "text"},
                        }
                    },
                    "deprecated": {"type": "boolean"},
                    "specifiedsubstance": {
                        "properties": {
                            "uuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "constituents": {
                                "properties": {
                                    "uuid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "substance": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "refPname": {"type": "text"},
                                            "refuuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "substanceClass": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "approvalID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "linkingID": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "name": {"type": "text"},
                                        }
                                    },
                                    "amount": {
                                        "properties": {
                                            "uuid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword",
                                            },
                                            "type": {"type": "text"},
                                            "high": {"type": "float"},
                                            "low": {"type": "float"},
                                            "units": {"type": "text"},
                                            "nonNumericValue": {"type": "text"},
                                            "average": {"type": "float"},
                                            "highLimit": {"type": "float"},
                                            "lowLimit": {"type": "float"},
                                        }
                                    },
                                    "references": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "role": {"type": "text"},
                                }
                            },
                            "references": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                        }
                    },
                    "tags": {"type": "text"},
                }
            }
        }
        return mapping
