import os
from time import sleep
import typing
from pysidian.core.base import core_mod
from sioDict import OneLayerDict, SioDict
from pysidian.utils.obsidian_vault_init import generate_default_vault, killObsidianProcess
from pysidian.utils.hash import hash_file
from pysidian.utils.misc import custom_uid, run_uri, walk_to_target
_system_appdata = os.getenv("APPDATA")
_system_appdata_obsidian = os.path.join(_system_appdata, "obsidian")
_system_obsidian_settings_path = os.path.join(_system_appdata_obsidian, 'obsidian.json')

vault_index_path = os.path.join(core_mod, "vault_index.json")
vault_index = OneLayerDict(vault_index_path)

vault_alias = OneLayerDict(os.path.join(core_mod, "vault_alias.json"))

class VaultConfig:
    def __init__(self, ref : 'Vault'):
        self.__ref = ref

    @property
    def app(self):
        return OneLayerDict(os.path.join(self.__ref.configFolder, "app.json"))
    
    @property
    def appearance(self):
        return OneLayerDict(os.path.join(self.__ref.configFolder, "appearance.json"))
    
    @property
    def corePlugins(self):
        return OneLayerDict(os.path.join(self.__ref.configFolder, "core-plugins.json"))
    
    @property
    def communityPlugins(self):
        return OneLayerDict(os.path.join(self.__ref.configFolder, "community-plugins.json"))
    
    @property
    def corePluginsMigration(self):
        return OneLayerDict(os.path.join(self.__ref.configFolder, "core-plugins-migration.json"))

class VaultMeta(type):
    _instances : typing.Dict[str, str] = {}
    _lastHash : str = None
    _lastDict : SioDict = None

    def isIndexed(cls, path : str = None, id : str = None):
        if not path and not id:
            return False
        
        if id and id in vault_index:
            return True

        if path and path in vault_index.values():
            return True
        
        return False
    
    def checkIdCollision(cls, id : str, path : str):
        if id in vault_index and vault_index[id] != path:
            return True
        
        if id in cls.getObsidianSettings()["vaults"]:
            if cls.getObsidianSettings()["vaults"][id]["path"] != path:
                return True

        return False

    def isObsidianIndexed(cls, path : str = None, id : str = None):
        if not path and not id:
            return False
        
        obsidianSetting = cls.getObsidianSettings()

        if id and id in obsidianSetting["vaults"]:
            return True

        if path:
            for id, meta in obsidianSetting["vaults"].items():
                if meta["path"] == path:
                    return True
        
        return False
    
    def getObsidianSettings(cls):
        if not os.path.exists(_system_obsidian_settings_path):
            return None

        newHash = hash_file(_system_obsidian_settings_path)

        if cls._lastDict is None or newHash != cls._lastHash:
            cls._lastDict = SioDict(_system_obsidian_settings_path)
            cls._lastHash = newHash

        return cls._lastDict
    
    def syncIndexes(cls):
        for id, meta in cls.getObsidianSettings()["vaults"].items():
            if id in vault_index and meta["path"] != vault_index[id]:
                vault_index[id] = meta["path"]
        
    def __call__(cls, path : str= None, id : str = None):
        cls.syncIndexes()

        if path is None and id is None:
            res = walk_to_target(".obsidian", os.getcwd(), 3)
            if not res:
                raise ValueError("Invalid path")
            
            path = os.path.dirname(res)

        if path is None and id is not None and id in vault_index:
            path = vault_index[id]

        if id is None:
            if path in vault_index.values():
                for id in vault_index:
                    if vault_index[id] == path:
                        break
            else:
                id = custom_uid(path)
                if cls.checkIdCollision(id, path):
                    raise ValueError("Id collision")

        if path is None:
            raise ValueError("Invalid path")

        path = os.path.abspath(path)
        if path not in cls._instances:
            cls._instances[path] = super(VaultMeta, cls).__call__(path, id)

        return cls._instances[path]

class Vault(metaclass=VaultMeta):
    @classmethod
    def fetch(
        cls, 
        alias : str = None,
        path : str = None, 
        id : str = None
    ):
        if alias and alias in vault_alias:
            id = vault_alias[alias]

        if id and id in vault_index:
            path = vault_index[id]
            return cls(path, id)
        
        if id:
            return None

        if path and path in vault_index.values():
            for id in vault_index:
                if vault_index[id] == path:
                    break
            return cls(path, id)

    @property
    def path(self):
        return self.__path
    
    @property
    def id(self):
        return self.__id

    def __init__(
        self, 
        path : str = None,
        id : str = None, 
    ):
        self.__path = path
        self.__id = id
        generate_default_vault(self.__path)

    @property
    def configFolder(self):
        return os.path.join(self.__path, ".obsidian")

    def openFolder(self):
        os.startfile(self.__path)

    @property
    def indexed(self):
        return self.__class__.isIndexed(self.__path, self.__id)
    
    @indexed.setter
    def indexed(self, value : bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be a boolean")

        if value:
            vault_index[self.__id] = self.__path
        else:
            del vault_index[self.__id]

    @property
    def obsidianIndexed(self):
        return self.__class__.isObsidianIndexed(self.__path, self.__id)
    
    @obsidianIndexed.setter
    def obsidianIndexed(self, value : bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be a boolean")

        if value:
            self.__class__.getObsidianSettings()["vaults"][self.__id] = {
                "path" : self.__path,
                "ts" : int(os.path.getmtime(self.__path))
            }

        else:
            del self.__class__.getObsidianSettings()["vaults"][self.__id]


    def open(self):
        if self.obsidianIndexed:
            return run_uri(f"obsidian://open?vault={self.id}")

        killObsidianProcess()
        sleep(0.1)
        self.obsidianIndexed = True
        sleep(0.1)
        run_uri(f"obsidian://open?vault={self.id}")
        sleep(0.1)
        self.obsidianIndexed = False
        
    @property
    def alias(self):
        ret = []
        for k, v in vault_alias.items():
            if v == self.id:
                ret.append(k)
        return ret
    
    @alias.setter
    def alias(self, value : typing.List[str]):
        for v in value:
            dict.__setitem__(vault_alias, v, self.id)

        vault_alias._save()

    
