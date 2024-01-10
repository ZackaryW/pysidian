import json
import os
import time
from pysidian.utils import mod_dir, obsidian_settings
import zipfile
import hashlib
from pysidian.utils.dict import getJson, writeJson

def custom_uid(text : str):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

def new_vault(name : str, path : str = os.getcwd()):
    os.makedirs(os.path.join(path, name), exist_ok=True)
    
    with zipfile.ZipFile(os.path.join(mod_dir, "obsidian_template.zip") , 'r') as zip_ref:
        zip_ref.extractall((fullpath := os.path.join(path, name)))
        
    return fullpath
        
def register_vault(path : str):
    osetting = getJson(obsidian_settings)
    cuid = custom_uid(path)
    # check already registered
    for uid, meta in osetting["vaults"].items():
        if meta["path"] == path:
            return uid

        if cuid == uid:
            raise Exception("There exists a vault with the same uid")
    
    writeJson({"vaults" : {cuid : {"path" : path, "ts" : int(time.time())}}}, obsidian_settings)
    
    return cuid

def unregister_vault_via_uid(uid :str):
    osetting = getJson(obsidian_settings)
    del osetting["vaults"][uid]
    with open(obsidian_settings, "w") as f:
        json.dump(osetting, f)
    
def unregister_vault_via_path(path : str):
    osetting = getJson(obsidian_settings)
    for uid, meta in osetting["vaults"].items():
        if meta["path"] == path:
            del osetting["vaults"][uid]
            break
    with open(obsidian_settings, "w") as f:
        json.dump(osetting, f)