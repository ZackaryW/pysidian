import toml
import os
import json

def json_load(path : str):
    with open(path, 'r') as f:
        return json.load(f)
    
def json_dump(data : dict, path : str):
    with open(path, 'w') as f:
        json.dump(data, f)

_raises = object()

def getVal(data : dict, key : str, default = _raises):
    if "::" not in key:
        return data[key]
    
    keys = key.split("::")
    target= data
    
    for k in keys:
        if k not in target:
            if default is _raises:
                raise Exception("key not found: " + key)
            
            return default
        target = target[k]
        
    return target


_history = {}
_cache = {}

def getDict(path : str, method = toml.load):
    global _history, _cache
    
    if path not in _history or os.path.getmtime(path) != _history[path]:
        _cache[path] = method(path)
        _history[path] = os.path.getmtime(path)
        
    return _cache[path]

def getToml(path : str):
    return getDict(path)

def getJson(path : str):
    return getDict(path, json_load)
    
def recursDictUpdate(dict1, dict2):
    for k, v in dict2.items():
        if k in dict1 and isinstance(dict1[k], dict) and isinstance(v, dict):
            recursDictUpdate(dict1[k], v)
        else:
            dict1[k] = v
            

def writeDict(
    config : dict,
    path : str,
    dumpMethod = toml.dump,
    loadMethod = toml.load
):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            dumpMethod(config, f)
            
        return
    
    existing : dict = getDict(path, loadMethod)

    recursDictUpdate(existing, config)
    
    with open(path, 'w') as f:
        dumpMethod(existing, f)

def writeToml(config : dict, path : str):
    writeDict(config, path, toml.dump, toml.load)
    
def writeJson(config : dict, path : str):
    writeDict(config, path, json.dump, json_load)