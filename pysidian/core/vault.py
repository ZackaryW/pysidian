from functools import cached_property
import os
from time import sleep
import typing
from pysidian.core.index import (
    current_vault_index, current_vault_alias, _vault_index_file,
    current_data_dir, system_obsidian_settings
)
from pysidian.core.vaultConfig import VaultConfig
from pysidian.utils import custom_uid, run_uri
import shutil
import zipfile
import psutil

class VaultMeta(type):
    _instances = {}

    def __call__(self, path: str, id: str = None):
        if not os.path.isdir(path):
            raise Exception(f"{path} is not a directory")

        if not os.path.exists(os.path.join(path, ".obsidian")):
            raise Exception(f"{path} is not an Obsidian vault")

        path = os.path.abspath(path)
        lid = Vault.locateId(path)
        if lid in self._instances:
            return self._instances[lid]

        if lid is not None:
            fid = lid
        elif id is not None and id in current_vault_index:
            raise Exception(f"{id} collision error")
        elif id is not None:
            fid = id
        else:
            fid = custom_uid(path)
            if fid in current_vault_index:
                raise Exception(f"{self.__id} collision error")

        if fid not in current_vault_index:
            current_vault_index[fid] = {
                "path": path, "ts": int(os.path.getmtime(path)*1000)
            }
            
        ins = super().__call__(path, fid)
        self._instances[fid] = ins
        return ins

class Vault(metaclass=VaultMeta):
    def __init__(self, path: str, id: str = None):


        self.__path = path
        
        self.__id = id

        self.config

    @classmethod
    def init(cls, path: str):
        if os.path.exists(path) and os.path.exists(os.path.join(path, ".obsidian")):
            path = os.path.abspath(path)
            return Vault(path)

        os.makedirs(os.path.join(path, ".obsidian"), exist_ok=True)
        return Vault(path)

    def reset(self, keepContent : bool = False):
        """
        reset the vault
        """
        if keepContent:
            shutil.rmtree(os.path.join(self.__path, ".obsidian"))
        else:
            shutil.rmtree(self.__path)
        os.makedirs(self.__path, exist_ok=True)
        with zipfile.ZipFile(os.path.join(current_data_dir, "obsidian_template.zip"), 'r') as zipObj:
            zipObj.extractall(self.__path)

    def openFolder(self):
        os.startfile(self.__path)

    def reg(self):
        if self.id not in system_obsidian_settings.get("vaults", {}):
            system_obsidian_settings["vaults"][self.id] = {
                    "path" : self.__path,
                    "ts" : self.ts
            }

    @property
    def isreg(self):
        return self.id in system_obsidian_settings.get("vaults", {})

    def unreg(self):
        if self.id in system_obsidian_settings.get("vaults", {}):
            del system_obsidian_settings["vaults"][self.id]

    def open(self):
        """
        open the vault
        """
        not_reg = not self.isreg

        if not_reg:
            self.reg()
            # detect obsidian instances and kill all
            Vault.kill()

        run_uri(f"obsidian://open?vault={self.id}")

        if not_reg:
            sleep(0.2)
            self.unreg()

    @classmethod
    def kill(cls):
        for proc in psutil.process_iter():
            if proc.name() == "Obsidian.exe":
                proc.kill()
        sleep(0.2)


    @property
    def ts(self):
        """
        last modified timestamp
        """
        return int(os.path.getmtime(self.__path)*1000)

    @property
    def id(self):
        return self.__id

    @cached_property
    def name(self):
        return os.path.basename(self.__path).split(".")[0]

    @property
    def aliases(self):
        ret = []
        for k, v in current_vault_alias.items():
            if v == self.id:
                ret.append(k)

        return ret

    @aliases.setter
    def aliases(self, value: typing.Union[str, tuple]):
        if isinstance(value, str):
            if value not in current_vault_alias:
                current_vault_alias[value] = self.id
            else:
                raise Exception(f"{value} already exists")

        if isinstance(value, tuple):
            pending_delete = []
            for existing in self.aliases:
                if existing not in value:
                    pending_delete.append(existing)

            for k in pending_delete:
                del current_vault_alias[k]

            needAdd = set(value) - set(pending_delete)

            for k in needAdd:
                current_vault_alias[k] = self.id

    @classmethod
    def getVault(cls, query: str):
        if len(query) == 16 and query in current_vault_index:
            return Vault(current_vault_index[query]["path"], query)

        if os.path.exists(query):
            return Vault(query)

        if query in current_vault_alias:
            id = current_vault_alias[query]
            return Vault(current_vault_index[id]["path"], id)

        for k, v in current_vault_index.items():
            path = v["path"]
            basename = os.path.basename(path)
            if basename == query:
                return Vault(path, k)

        raise Exception(f"{query} not found")

    @staticmethod
    def checkObsolete():
        with _vault_index_file.saveLock():
            for k, v in current_vault_index.items():
                if not os.path.exists(v["path"]):
                    del current_vault_index[k]

    @cached_property
    def config(self):
        return VaultConfig(os.path.join(self.__path, ".obsidian"))

    @classmethod
    def locateId(cls, path : str):
        for k, v in current_vault_index.items():
            if v["path"] == path:
                return k

    def installPlugin(self, id : str, src : str):
        pluginDir = os.path.join(self.__path, ".obsidian", "plugins", id)
        if os.path.isdir(src):
            shutil.copytree(src, pluginDir, dirs_exist_ok=True)
        elif src.endswith(".zip"):
            with zipfile.ZipFile(src, 'r') as zip_ref:
                zip_ref.extractall(pluginDir)

        else:
            raise Exception(f"{src} not supported")
