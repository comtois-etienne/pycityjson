

def get_attribute(data, key, *, default=None):
    if key in data:
        return data[key]
    return default

def get_nested_attribute(data, key_a, key_b, *, default=None):
    if key_a in data and key_b in data[key_a]:
        return data[key_a][key_b]
    return default

def round_attribute(data, attribute, decimals=0):
    if attribute in data:
        data[attribute] = round(data[attribute], decimals)
    if decimals == 0:
        data[attribute] = int(data[attribute])

