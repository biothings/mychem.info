import csv, os
from biothings.utils.dataload import dict_sweep, unlist

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

def custom_dict_sweep(data):
    if isinstance(data, list):
        if len(data) == 1:
            return custom_dict_sweep(data[0])
        else:
            return [custom_dict_sweep(item) for item in data]
    elif isinstance(data, dict):
        return {key: custom_dict_sweep(val) if isinstance(val, (list, dict)) else val for key, val in data.items()}
    else:
        return data

def load_products(_file):
    f = open(_file,'r',encoding="latin1")
    reader = csv.DictReader(f,dialect='excel-tab')
    for row in reader:
        _dict = product_restr_dict(row)
        _dict = convert_to_unicode(custom_dict_sweep(_dict))
        _dict["_id"] = _dict["ndc"]["productndc"]
        yield _dict

def load_packages(_file):
    f = open(_file,'r',encoding='latin1')
    reader = csv.DictReader(f,dialect='excel-tab')
    for row in reader:
        _dict = package_restr_dict(row)
        _dict = unlist(custom_dict_sweep(_dict))
        _dict["_id"] = _dict["ndc"]["productndc"]
        yield _dict

def load_data(data_folder):
    print(load_data)
    pharm_classes_list = []
    cs_list = []
    moa_list = []  

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


        for item in doc:                
                ndc_data = doc.get('ndc', {})
                # Check if 'pharm_classes' exists in the 'ndc' dictionary
                if isinstance(ndc_data, dict) and 'pharm_classes' in ndc_data:
                    # Get the 'pharm_classes' value
                    pharm_classes = ndc_data['pharm_classes']
                else:
                    print("Pharm Classes not found in the data.")
          
                # Extract 'cs' and 'moa' from each item
                if isinstance(pharm_classes, str):
                    element_list = pharm_classes.split(', ')

                for element in element_list:
                    if element.strip().lower().endswith('[cs]'):
                        cs_value = element.split('[cs]')[0].strip()
                        if cs_value not in cs_list:
                            cs_list.append(cs_value)

                        
                    if element.strip().lower().endswith('[moa]'):
                        moa_value = element.split('[moa]')[0].strip()
                        if moa_value not in moa_list:
                            moa_list.append(moa_value)


    if cs_list != []:
        doc["ndc"]["pharm_classes"] = {
        "CS": list(cs_list)
    }                 

    if moa_list != []:
        doc["ndc"]["pharm_classes"] = {
        "MOA": list(moa_list)
    }       

    yield doc


src_dir = os.path.dirname(os.path.abspath(__file__))
d_folder = os.path.abspath(os.path.join(src_dir, "..","..","..","..","..", "data_folder"))

for processed_data_item in load_data(d_folder):
    pass
