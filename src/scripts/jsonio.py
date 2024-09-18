import json


def read_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            str_json = json.load(json_file)
    except Exception as e:
        print(f'Error reading JSON file: {e}')
        return None
    return str_json


def write_json(str_json, file_path, indent=0):
    try:
        with open(file_path, 'w') as json_file:
            if indent > 0:
                json.dump(str_json, json_file, indent=indent)
            else:
                json.dump(str_json, json_file)
    except Exception as e:
        print(f'Error writing JSON file: {e}')

