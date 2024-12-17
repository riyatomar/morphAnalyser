import json

def read_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data["sentences"]

def read_parser_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)["response"]

def save_to_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
