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
        #print(doc)
        yield doc

def print_list():
     # Get the path to the parent directory of the current script (i.e., src directory)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # Go several levels up to access the data_folder
    data_folder = os.path.abspath(os.path.join(src_dir, "..","..","..","..","..", "data_folder"))

    # Call the load_data function with the folder path as an argument
    try:
        data_generator = load_data(data_folder)
        data_list = list(data_generator)  
        pharm_classes_list = []
        for item in data_list:
            if 'pharm_classes' in item['ndc']:
                pharm_classes_list.append(item['ndc']['pharm_classes'])
               
                cs_list = []
                moa_list = []

        # Iterate through each element to check if it ends with "CS" or "MoA"
        for element in pharm_classes_list:
            element_list = element.split(', ')
            for item in element_list:
                if item.endswith('[CS]'):
                    cs_list.append(item)
                if item.endswith('[MoA]'):
                    moa_list.append(item)

        # Convert lists to sets to get unique values
        unique_cs = set(cs_list)
        unique_moa = set(moa_list)

        # Print the resulting unique lists
        with open("cs_values.txt", "w") as cs_file:
            cs_file.write("\n".join(unique_cs))

        with open("moa_values.txt", "w") as moa_file:
            moa_file.write("\n".join(unique_moa))
   
    except FileNotFoundError:
        print(f"Error: Could not find the specified folder '{data_folder}'.")


print_list()