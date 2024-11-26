def check_non_null_values(data: dict | list):
    values = data if isinstance(data, list) else list(data.values())

    for value in values:
        if value is None:
            return False

        if isinstance(value, dict) or isinstance(value, list):
            if not check_non_null_values(value):
                return False

    return True


def get_null_keys(data: dict):
    keys = []

    for key, value in data.items():
        if not value:
            keys.append(key)

    return keys
