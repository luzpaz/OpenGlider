import json
import re
import time
import openglider

__ALL__ = ['dumps', 'dump', 'loads', 'load']

# Main json-export routine.
# Maybe at some point it can become necessary to de-reference classes with _module also,
# because of same-name-elements....
# For the time given, we're alright


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if obj.__class__.__module__ == 'numpy':
            return obj.tolist()
        elif hasattr(obj, "__json__"):
            return {"_type": obj.__class__.__name__,
                    "_module": obj.__class__.__module__,
                    "data": obj.__json__()}
        else:
            return super(Encoder, self).default(obj)


def get_element(_module, _name):
    for rex in openglider.config["json_forbidden_modules"]:
        if re.match(rex, _module):
            raise Exception
        elif re.match(rex, _name):
            raise Exception
    for rex in openglider.config["json_allowed_modules"]:
        match = re.match(rex, _module)
        if match:
            module = __import__(_module, fromlist=_module.split("."))
            if hasattr(module, _name):
                obj = getattr(module, _name)
                return obj
            else:
                raise LookupError("No element of type {} found (module: {})".format(_name, _module))


def object_hook(dct):
    """
    Return the de-serialized object
    """
    if '_type' in dct and '_module' in dct:
        obj = get_element(dct["_module"], dct["_type"])

        try:
            # use the __from_json__ function if present. __init__ otherwise
            deserializer = getattr(obj, '__from_json__', obj)
            return deserializer(**dct['data'])
        except TypeError as e:
            raise TypeError("{} in element: {} ({})".format(e, dct["_type"], dct["_module"]))

    else:
        return dct


def add_metadata(data):
    if isinstance(data, dict) and 'MetaData' in data:
        data['MetaData']['date_modified'] = time.strftime("%d.%m.%y %H:%M")
        return data
    else:
        return {'MetaData': {'application': 'openglider',
                             'version': openglider.__version__,
                             'author': openglider.config["user"],
                             'date_created': time.strftime("%d.%m.%y %H:%M"),
                             'date_modified': time.strftime("%d.%m.%y %H:%M")},
                'data': data}


def dumps(obj):
    return json.dumps(add_metadata(obj), cls=Encoder)


def dump(obj, fp):
    return json.dump(add_metadata(obj), fp, cls=Encoder, indent=4)


def loads(obj):
    return json.loads(obj, object_hook=object_hook)


def load(fp):
    return json.load(fp, object_hook=object_hook)