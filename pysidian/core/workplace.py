
from functools import cached_property
import os
import shutil
from packaging import version
import typing
import zipfile
import orjson
from sioDict import SioDict
from pysidian.core.base import core_mod
from pysidian.utils.misc import walk_to_target
from pysidian.core.vault import Vault
from pysidian.data import getFile

plugin_indexes : typing.Dict[str, 'PluginIndexEntry'] = SioDict(os.path.join(core_mod, "plugin_indexes.json"))

class PluginIndexEntry(typing.TypedDict):
    id : str
    latestVersion : str
    subscribedVaults : typing.List[str]

class PysidianConfig(typing.TypedDict):
    testVaults : typing.Dict[str, str]
    workDir : str

class PluginWorkplaceMeta(type):
    _instances : typing.Dict[str, str] = {}

    def __call__(cls, path : str) -> 'PluginWorkplace':
        if path in cls._instances:
            return cls._instances[path]

        try:
            if ".pysidian" in path:
                path = os.path.dirname(path)

            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        except Exception:
            raise ValueError("Invalid path")

        path = os.path.abspath(path)

        # for all other child folders
        for folder in os.listdir(path):
            if not os.path.isdir(os.path.join(path, folder)):
                continue

            if folder == ".pysidian":
                continue

            if (_k := walk_to_target(".pysidian", os.path.join(path, folder), 2)) is None:
                continue

            raise ValueError("Invalid path, a .pysidian folder contains in child folders")
            

        if path not in cls._instances:
            cls._instances[path] = super(PluginWorkplaceMeta, cls).__call__(path)

        return cls._instances[path]

class PluginWorkplaceConfig:
    def __init__(self, ref : 'PluginWorkplace'):
        self.__ref = ref
        self.__config = SioDict(os.path.join(self.__ref.path, ".pysidian", "config.json"))
        os.makedirs(os.path.join(self.path, "release"), exist_ok=True)

        with self.__config.saveLock():
            if "testVaults" not in self.__config:
                self.__config["testVaults"] = {}
            
            if "stagingDir" not in self.__config:
                self.__config["stagingDir"] = "output"

            if "stagingCmd" not in self.__config:
                self.__config["stagingCmd"] = "npm run build"

    @property
    def path(self):
        return os.path.join(self.__ref.path, ".pysidian")

    @property
    def testVaultsStr(self) ->list:
        return list(self.__config.get("testVaults", {}).keys())  

    @property
    def testVaults(self) -> typing.List[Vault]:
        return [Vault(os.path.join(self.__ref.path, path), id) for id, path in self.__config.get("testVaults", {}).items()]

    @testVaults.setter
    def testVaults(self, value : typing.List[Vault]):
        self.__config["testVaults"] = {vault.id : os.path.relpath(vault.path, self.__ref.path) for vault in value}

    @property
    def stagingDir(self):
        return os.path.join(self.__ref.path, self.__config["stagingDir"])
    
    @stagingDir.setter
    def stagingDir(self, value : str):
        self.__config["stagingDir"] = value

    @property
    def stagingCmd(self):
        return self.__config["stagingCmd"]

    @stagingCmd.setter
    def stagingCmd(self, value : str):
        self.__config["stagingCmd"] = value

    @cached_property
    def manifestPath(self) -> str:
        for sss in os.listdir(self.__ref.path):
            if os.path.isdir(os.path.join(self.__ref.path, sss)):
                continue

            if sss == "manifest.json":
                return os.path.join(self.__ref.path, sss)
                
        return None

    @property
    def manifest(self):
        with open(self.manifestPath, "rb") as f:
            return orjson.loads(f.read())

    @property
    def manifestVersion(self):
        versionText =  self.manifest["version"]
        return version.parse(versionText)
    
    @property
    def releaseVersions(self):
        if len(os.listdir(os.path.join(self.path, "release"))) == 0:
            return []
        ret = []
        for vfile in os.listdir(os.path.join(self.path, "release")):
            if not vfile.endswith(".zip"):
                continue

            ret.append(vfile[:-4])

        ret = [version.parse(v) for v in ret]
        #sort by biggest version
        ret.sort(key=lambda x: x, reverse=True)
        return ret
    
    @property
    def latestRelease(self):
        return self.releaseVersions[0] if len(self.releaseVersions) > 0 else None
    
    @property
    def latestReleasePath(self):
        if self.latestRelease is None:
            return None
        
        stringLatest = f"{self.latestRelease.major}.{self.latestRelease.minor}.{self.latestRelease.micro}"

        return os.path.join(self.path, "release", f"{stringLatest}.zip")

    @property
    def indexIntel(self):
        if self.__ref.path not in plugin_indexes:
            return None

        return plugin_indexes[self.__ref.path]

class PluginWorkplace(metaclass=PluginWorkplaceMeta):
    @classmethod
    def get(cls, path : str = None):
        if path is None:
            path = os.getcwd()

        p = walk_to_target(".pysidian", path, 3)
        if p is not None:
            return cls(p)


    @classmethod
    def create(cls, path : str = None):
        if path is None:
            path = os.getcwd()

        return cls(path)
    
    @classmethod
    def createFromSample(cls, path : str = None):
        if path is None:
            path = os.getcwd()

        os.makedirs(os.path.join(path, ".pysidian"), exist_ok=True)
        if len(os.listdir(path)) < 13:
            with zipfile.ZipFile(getFile("sample_plugin.zip"), 'r') as zip_ref:
                zip_ref.extractall(path)

        return cls(path)

    def __init__(self, path : str):
        self.__path = path
        self.__globalState = self.config.manifest.get(self.__path, None) is not None

    @property
    def path(self):
        return self.__path

    @cached_property
    def config(self):
        return PluginWorkplaceConfig(self)

    def addLocalTestVault(self, name : str):
        vault = Vault(os.path.join(self.path, name))
        self.config.testVaults = self.config.testVaults + [vault]
        return vault

    def setGlobal(self):
        if self.__globalState:
            return
        
        plugin_indexes[self.path] = {
            "id" : self.config.manifest["id"],
            "latestVersion" : self.config.manifest["version"],
            "subscribedVaults" : []
        }

        self.__globalState = True

    def unsetGlobal(self):
        if not self.__globalState:
            return

        del plugin_indexes[self.path]

        self.__globalState = False

    def subscribeVault(self, vault : Vault):
        if not self.__globalState:
            raise ValueError("Can only subscribe to global plugins")

        plugin_indexes[self.path]["subscribedVaults"].append(vault.id)
    
    def stage(self):
        lastCwd = os.getcwd()

        os.chdir(self.path)
        os.system("npm install")
        os.system(self.config.stagingCmd)
        os.chdir(lastCwd)

    def commit(self, raises : bool = False):
        # Check if the current manifest version is older than the latest release
        if self.config.latestRelease is not None and self.config.manifestVersion <= self.config.latestRelease:
            if raises:
                raise ValueError("Manifest version is older than latest release")
            else:
                return

        # Ensure the staging directory exists
        os.makedirs(self.config.stagingDir, exist_ok=True)

        # Define a list of files to potentially copy to the staging directory
        files_to_copy = ["main.js", "styles.css"]
        for file_name in files_to_copy:
            source_path = os.path.join(self.path, file_name)
            if os.path.exists(source_path):
                shutil.copy(source_path, os.path.join(self.config.stagingDir, file_name))

        # Always copy the manifest.json file
        shutil.copyfile(self.config.manifestPath, os.path.join(self.config.stagingDir, "manifest.json"))

        # Create the release directory if it doesn't exist
        release_dir = os.path.join(self.config.path, "release")
        os.makedirs(release_dir, exist_ok=True)

        # Create the zip file in the release directory
        manifestVer = self.config.manifestVersion
        stringManifestVer = f"{manifestVer.major}.{manifestVer.minor}.{manifestVer.micro}"
        zip_file_path = os.path.join(release_dir, f"{stringManifestVer}.zip")
        with zipfile.ZipFile(zip_file_path, 'w') as zip_ref:
            for root, dirs, files in os.walk(self.config.stagingDir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_ref.write(file_path, os.path.relpath(file_path, self.config.stagingDir))

    def push(self, version : str = None):
        pending = []

        for vault in self.config.testVaults:
            pending.append(vault.path)

        if self.__globalState:
            pending.extend(plugin_indexes[self.path]["subscribedVaults"])

        pending = list(set(pending))

        if len(pending) == 0:
            return
        
        if version is not None:
            releasePath = os.path.join(self.config.path, "release", f"{version}.zip")
            if not os.path.exists(releasePath):
                raise ValueError("Release version does not exist")
        else:
            releasePath = self.config.latestReleasePath    
        

        if releasePath is None:
            raise ValueError("No release path found")

        with zipfile.ZipFile(releasePath, 'r') as zip_ref:
            for path in pending:
                if not os.path.exists(os.path.join(path, ".obsidian")):
                    continue

                target_plugin_dir = os.path.join(path, ".obsidian", "plugins", self.config.manifest.get("id"))
                os.makedirs(
                    target_plugin_dir, 
                    exist_ok=True
                )

                zip_ref.extractall(target_plugin_dir)

    def openFolder(self):
        os.startfile(self.path)

