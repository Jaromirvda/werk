import json


def update_json_file(filepath, id):
    with open(filepath, 'r') as file:
        data = json.load(file)

    data['gpus'] = [gpu for gpu in data['gpus'] if gpu['id'] != id or gpu['series'] != 'created series']

    with open(filepath, 'w') as file:
        json.dump(data, file)