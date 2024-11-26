import json


def json_to_named_entity_relational(json_data):
    return (
        json.dumps(json_data)
        .replace('"text"', "text")
        .replace('"float"', "float")
        .replace('"int"', "int")
        .replace('"list"', "list")
    )
