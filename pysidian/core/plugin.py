from functools import cached_property
import os
import shutil
from typing import TypedDict
import typing
from pysidian.core.index import (
    current_plugin_index, current_plugin_alias,
    current_vault_index, current_data_dir,_vault_index_file
)
from pysidian.core.vault import Vault
from pysidian.utils import load_json
from sioDict import SioDict
import zipfile
from packaging import version

class PluginEntry(TypedDict, total=False):
    installed : typing.List[str]
    latestVer : str
    id : str

class PluginConfig(TypedDict):
    workDir : str

class PluginManifest(TypedDict):
    id : str
    name : str
    version : str
    description : str
    author : str
    authorUrl : str


class Plugin:
    @classmethod
    def get(cls, query : str):
        if os.path.isdir(query) and os.path.exists(os.path.join(query, ".pysidian", "config.json")):
            return cls(query)
        elif query in current_plugin_alias:
            return cls(current_plugin_alias[query])
        else:
            for k, v in current_plugin_index.items():
                if "id" in v and v["id"] == query:
                    return cls(k)
    
    @classmethod
    def init(cls, cwd : str, workDir : str = "src") -> "Plugin":
        cwd = os.path.abspath(cwd)
        if cwd in current_plugin_index:
            return cls.get(cwd)
        if not os.path.isdir(cwd):
            raise Exception(f"{cwd} is not a directory")

        os.makedirs(os.path.join(cwd, ".pysidian"), exist_ok=True)
        sdict = SioDict(
            os.path.join(cwd, ".pysidian", "config.json"),
            workDir= workDir
        )

        plugin = cls(cwd)
        plugin.__dict__["pluginConfig"] = sdict
        return plugin

    @classmethod
    def sample(cls, cwd : str, workDir : str= "src"):
        target_zip = os.path.join(current_data_dir, "ob_sample.zip")
        os.makedirs(os.path.join(cwd, workDir), exist_ok=True)
        with zipfile.ZipFile(target_zip, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(cwd, workDir))
        
        return cls.init(cwd, workDir)

    def __init__(self, cwd : str):
        cwd = os.path.abspath(cwd)
        self.__cwd = cwd

        if self.__cwd not in current_plugin_index:
            current_plugin_index[self.__cwd] = PluginEntry(
                installed = []
            )

        # stating readiness
        os.makedirs(os.path.join(self.cwd, ".pysidian", "staging"), exist_ok=True)
        os.makedirs(os.path.join(self.cwd, ".pysidian", "releases"), exist_ok=True)

    @property
    def cwd(self):
        return self.__cwd

    @property
    def installedVaults(self):
        vaults= current_plugin_index.get(self.cwd, {}).get("installed", [])
        with _vault_index_file.saveLock():
            for vault in vaults:
                if vault not in current_vault_index:
                    current_vault_index[self.cwd, "installed"].remove(vault)

        return {x : Vault.getVault(x) for x in vaults}
    
    @property
    def stagingManifest(self) -> dict:
        try:
            return load_json(os.path.join(self.cwd, ".pysidian", "staging", "manifest.json"))
        except: # noqa
            return {}
    
    @property
    def stagingVersion(self):
        ver = self.stagingManifest.get("version", None)
        if not ver:
            return None
        ver = version.parse(ver)
        return ver

    @property
    def pluginManifest(self) -> PluginManifest:
        return load_json(os.path.join(self.cwd, self.pluginConfig.get("workDir", "src"), "manifest.json"))

    @property
    def pluginVersion(self):
        ver = self.pluginManifest.get("version", None)
        if not ver:
            return None
        ver = version.parse(ver)
        return ver

    @property
    def releaseVersions(self):
        return [
            x.split(".")[0] for x in os.listdir(os.path.join(self.cwd, ".pysidian", "releases"))
        ]
    
    @property
    def id(self):
        return self.pluginManifest.get("id", None)
    
    @property
    def workDir(self):
        return self.pluginConfig.get("workDir", "src")

    @cached_property
    def pluginConfig(self) -> PluginConfig:
        sdict = SioDict(
            os.path.join(self.cwd, ".pysidian", "config.json")
        )
        if "workDir" not in sdict:
            sdict["workDir"] = "src"
        return sdict

    @cached_property
    def pluginIndexEntry(self) -> typing.Union[PluginEntry, dict]:
        return current_plugin_index[self.cwd]

    def addVault(self, vault : Vault):
        if vault.id in current_plugin_index[self.cwd].get("installed", []):
            raise Exception(f"{vault.name} already installed")
        
        current_plugin_index[self.cwd]["installed"].append(vault.id)

    def _clearStagingFolder(self):
        shutil.rmtree(os.path.join(self.cwd, ".pysidian", "staging"))
        os.makedirs(os.path.join(self.cwd, ".pysidian", "staging"))

    def _createRelease(self):
        releasePath = os.path.join(self.cwd, ".pysidian", "releases", f"{self.stagingVersion}.zip")
        if os.path.exists(releasePath):
            raise Exception("release file already exists")

        with zipfile.ZipFile(releasePath, 'w') as zipObj:
            for root, _, files in os.walk(os.path.join(self.cwd, ".pysidian", "staging")):
                for file in files:
                    filePath = os.path.join(root, file)
                    zipObj.write(filePath, os.path.relpath(filePath, os.path.join(self.cwd, ".pysidian", "staging")))
        

    def _bkupExistingStagingArea(self):
        if not len(os.listdir(os.path.join(self.cwd, ".pysidian", "staging"))):
            return False
    

        pluginVersion = self.pluginVersion
        stagingVersion = self.stagingVersion
        releaseVersions = self.releaseVersions

        if pluginVersion is None:
            raise Exception("no plugin version")
        
        if stagingVersion is None:
            return False
        
        if pluginVersion == stagingVersion:
            raise Exception("already staged")
        
        if stagingVersion > pluginVersion:
            raise Exception("staging version is newer than plugin version")
        
        if pluginVersion in releaseVersions:
            raise Exception("plugin version already released")
        
        if stagingVersion in releaseVersions:
            return False
        
        self._createRelease()
        return True

    def stage(self):
        self._bkupExistingStagingArea()
        self._clearStagingFolder()

            
        src_path =os.path.join(self.cwd, self.pluginConfig.get("workDir", "src"))
        dst_path = os.path.join(self.cwd, ".pysidian", "staging")
        shutil.copytree(
            src_path,
            dst_path, dirs_exist_ok=True
        )
        
    def commit(self):
        try:
            self._createRelease()
        except: # noqa
            pass

        if "id" not in self.pluginIndexEntry:
            self.pluginIndexEntry["id"] = self.id

        stagingVersion = self.stagingManifest.get("version", None)
        if not stagingVersion:
            raise Exception("no staging version")
        
        latestEntryVersion = self.pluginIndexEntry.get("version", None)
        
        ver1 = version.parse(stagingVersion)
        ver2 = version.parse(latestEntryVersion) if latestEntryVersion else None

        if not latestEntryVersion:
            self.pluginIndexEntry["version"] = stagingVersion
        elif ver1 == ver2:
            raise Exception("already committed")
        elif ver1 > ver2:
            raise Exception("staging version is newer than plugin version")
        else:
            self.pluginIndexEntry["version"] = stagingVersion
        
    def push(self, version : str = None):
        stagingPushSrc = os.path.join(self.cwd, ".pysidian", "staging")
        
        if version is not None and version not in self.releaseVersions:
            raise Exception("version not available")

        targetZipPath = os.path.join(
            self.cwd, ".pysidian", "releases", f"{version}.zip"
        )

        for vault in self.installedVaults.values():
            if version is None:
                vault.installPlugin(self.id, stagingPushSrc)
            else:
                vault.installPlugin(self.id, targetZipPath)
        
