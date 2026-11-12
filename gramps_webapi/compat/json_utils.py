import json

import orjson

import gramps.gen.lib as lib
from gramps.gen.lib import serialize

NoneType = type(None)


class DataDict(dict):
    def __init__(self, data=None):
        if isinstance(data, dict):
            super().__init__(data)
        else:
            super().__init__()
            if data:
                self.update(object_to_data(data))

    def __str__(self):
        if "_object" not in self:
            self["_object"] = data_to_object(self)
        return str(self["_object"])

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(
                "this method cannot be used to access hidden attributes"
            )
        if key in self:
            value = self[key]
            if isinstance(value, dict):
                return DataDict(value)
            elif isinstance(value, list):
                return DataList(value)
            else:
                return value
        self["_object"] = data_to_object(self)
        return getattr(self["_object"], key)


class DataList(list):
    def __getitem__(self, position):
        value = super().__getitem__(position)
        if isinstance(value, dict):
            return DataDict(value)
        elif isinstance(value, list):
            return DataList(value)
        else:
            return value

    def __add__(self, value):
        return DataList([x for x in self] + [x for x in value])

    def __radd__(self, value):
        return DataList([x for x in value] + [x for x in self])


def remove_object(data):
    if isinstance(data, dict):
        return {
            key: remove_object(value)
            for key, value in data.items()
            if key != "_object"
        }
    elif isinstance(data, (list, tuple)):
        return [remove_object(item) for item in data]
    else:
        return data


def object_to_dict(obj):
    if isinstance(obj, (float, int, str, NoneType)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [object_to_dict(item) for item in obj]
    return json.loads(serialize.to_json(obj))


def object_to_data(obj):
    if isinstance(obj, (float, int, str, NoneType)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return DataList([object_to_data(item) for item in obj])
    data = json.loads(serialize.to_json(obj))
    data["_object"] = obj
    return DataDict(data)


def data_to_object(data):
    if isinstance(data, dict):
        if "_object" in data:
            return data["_object"]
        cleaned = {k: data_to_object(v) for k, v in data.items()}
        return serialize.from_json(json.dumps(remove_object(cleaned)))
    elif isinstance(data, (list, tuple)):
        return [data_to_object(item) for item in data]
    return data


def object_to_string(obj):
    return serialize.to_json(obj)


def data_to_string(data):
    return orjson.dumps(remove_object(data)).decode()


def string_to_data(string):
    loaded = orjson.loads(string)
    if isinstance(loaded, list):
        return loaded
    return DataDict(loaded)


def string_to_dict(string):
    return orjson.loads(string)


def string_to_object(string):
    if isinstance(string, bytes):
        string = string.decode()
    return serialize.from_json(string)
