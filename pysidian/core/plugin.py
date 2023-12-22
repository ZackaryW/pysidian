import os
from dataclasses import dataclass
import shutil
from zrcl3.orjson_io_fallback import save_json, load_json
import zipfile
from pysidian.core.vault import ObsidianVault
from packaging import version

@dataclass
class ObsidianPluginManifest:
    id : str
    name : str
    version : str
    minAppVersion : str
    description : str
    author : str
    authorUrl : str
    fundingUrl : str = None
    isDesktopOnly : bool = None
    
    def toDict(self):
        return {k : w for k, w in self.__dict__.items() if w is not None}
    
testManifest = ObsidianPluginManifest(
    id="pysidian-test-plugin",
    name="Test Plugin",
    version="1.0.0",
    minAppVersion="1.0.0",
    description="Test Plugin",
    author="Zack",
    authorUrl="https://github.com/zackaryw",
)
    
@dataclass(slots=True)
class ObsidianPlugin:
    path : str
    
    def __post_init__(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError
    
    @property
    def manifest(self):
        if not os.path.exists(os.path.join(self.path, "manifest.json")):
            return None
        return ObsidianPluginManifest(**load_json(os.path.join(self.path, "manifest.json")))
    
    @manifest.setter
    def manifest(self, value):
        if not isinstance(value, ObsidianPluginManifest):
            raise TypeError
        save_json(os.path.join(self.path, "manifest.json"), value.toDict())
    
    def toVault(self, vault : ObsidianVault):
        os.makedirs(os.path.join(vault.configDir, "plugins"), exist_ok=True)
        shutil.copytree(self.path, os.path.join(vault.configDir, "plugins", self.manifest.id))
        
    def bkup(self, path : str):
        # make a zip to target folder {name}{version}
        with zipfile.ZipFile(os.path.join(path, f"{self.manifest.name}{self.manifest.version}.zip"), 'w') as zipObj:
            for folderName, subfolders, filenames in os.walk(self.path):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath, os.path.relpath(filePath, os.path.join(self.path, '..')))
        
    def __get_target_vault_plugin_version(self, vault : ObsidianVault):
        if not os.path.exists(os.path.join(vault.configDir, "plugins", self.manifest.id, "manifest.json")):
            return None
        raw = load_json(os.path.join(vault.configDir, "plugins", self.manifest.id, "manifest.json"))
        return raw["version"]
        
                    
    def update(self, vault : ObsidianVault):
        targetVersion = self.__get_target_vault_plugin_version(vault)
        if targetVersion is None:
            return self.toVault(vault)
        
        vaultVersion = version.parse(targetVersion)
        repoVersion = version.parse(self.manifest.version)
        
        if vaultVersion > repoVersion:
            print("Plugin {} is newer in the vault".format(self.manifest.id))
        elif vaultVersion == repoVersion:
            print("Plugin {} is the same version in the vault".format(self.manifest.id))
        else:
            print(f"updating plugin {self.manifest.id} from {vaultVersion} to {repoVersion}")
        
            self.toVault(vault)
    
