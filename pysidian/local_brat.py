
from functools import cache
import os
import hashlib
import shutil
import json
from pysidian.utils.dict import getJson

def gen_plugin_checksum(pluginDir : str):
    main = hashlib.md5(open(os.path.join(pluginDir, "main.js"), 'rb').read()).hexdigest()
    manifest = hashlib.md5(open(os.path.join(pluginDir, "manifest.json"), 'rb').read()).hexdigest()
    try:
        styles = hashlib.md5(open(os.path.join(pluginDir, "styles.css"), 'rb').read()).hexdigest()
    except: # noqa
        styles = "XXX"

    combinedhash = main + manifest + styles
    return combinedhash

def getLocalBratPkgs(vaultdir : str):
    pkgPath = os.path.join(vaultdir, ".obsidian","plugins", "local-brat", "pkgs.json")
    
    if not os.path.exists(pkgPath):
        with open(pkgPath, "w") as f:
            f.write('{}')
        pkgs = {}    
    else:
        pkgs = getJson(pkgPath)
        
    return pkgs, pkgPath

@cache
def getPluginId(plugindir : str):
    pluginManifest = getJson(os.path.join(plugindir, "manifest.json"))
    return pluginManifest["id"]

def copyPlugin(vaultdir : str, plugindir : str):
    pluginid = getPluginId(plugindir)
    dstPluginDir = os.path.join(vaultdir, ".obsidian","plugins", pluginid)
    
    if os.path.exists(dstPluginDir):
        shutil.rmtree(dstPluginDir)

    shutil.copytree(
        plugindir, dstPluginDir,
        # ignore localBrat file
        ignore=lambda dir, files: ["localBrat"]
    )
    
    pkgs, pkgPath = getLocalBratPkgs(vaultdir)
    pkgs[pluginid] = {
        "checksum" : gen_plugin_checksum(plugindir),
        "path" : plugindir
    }
    with open(pkgPath, "w") as f:
        f.write(json.dumps(pkgs))
    
    
def updatePlugin(vaultdir : str, plugindir : str):
    pkgs, pkgPath = getLocalBratPkgs(vaultdir)
        
    pluginId = getPluginId(plugindir)
    
    if pluginId not in pkgs:
        return copyPlugin(vaultdir, plugindir)
        
    alr_checksum = pkgs[pluginId]["checksum"]
    
    new_checksum = open(os.path.join(plugindir, "localBrat")).read().strip()
    
    if alr_checksum == new_checksum:
        return
    
    copyPlugin(vaultdir, plugindir)
    