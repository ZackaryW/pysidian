from dataclasses import dataclass
import os
import shutil
import time
from pysidian.core.utils import run_uri, sixteen_characters_hash, split_path_at_last_separator
from pysidian.core.app import obsidianApp, VaultCtx
from zrcl3.orjson_io_fallback import save_json

@dataclass(slots=True)
class ObsidianVault:
    name : str
    path : str
    uid : str
    
    @property
    def vaultDir(self):
        return os.path.join(self.path, self.name)
    
    @property
    def configDir(self):
        return os.path.join(self.vaultDir, '.obsidian')
    
    def reset(self):
        try:
            shutil.rmtree(self.vaultDir)
        except: # noqa
            pass
        self.__internal_new_dir()
        self.__internal_write_files()
        
    def __internal_new_dir(self):
        os.makedirs(self.vaultDir, exist_ok=True)
        os.makedirs(self.configDir, exist_ok=True)
        
    def __internal_write_files(self):
        # write config files

        # Save an empty dictionary to 'app.json'
        save_json(os.path.join(self.configDir, 'app.json'), {})

        # Save a dictionary with initial settings to 'appearance.json'
        save_json(os.path.join(self.configDir, 'appearance.json'), {"accentColor": ""})

        # Save a dictionary to 'core-plugins-migration.json'
        save_json(os.path.join(self.configDir, 'core-plugins-migration.json'), {
            "file-explorer": True,
            "global-search": False,
            "switcher": False,
            "graph": False,
            "backlink": False,
            "canvas": False,
            "outgoing-link": False,
            "tag-pane": False,
            "properties": False,
            "page-preview": False,
            "daily-notes": False,
            "templates": False,
            "note-composer": False,
            "command-palette": False,
            "slash-command": False,
            "editor-status": True,
            "bookmarks": False,
            "markdown-importer": False,
            "zk-prefixer": False,
            "random-note": False,
            "outline": False,
            "word-count": False,
            "slides": False,
            "audio-recorder": False,
            "workspaces": False,
            "file-recovery": False,
            "publish": False,
            "sync": False
        })

        # Save a list to 'core-plugins.json'
        save_json(os.path.join(self.configDir, 'core-plugins.json'), ["editor-status", "file-explorer"])

        # Save an empty dictionary to 'hotkeys.json'
        save_json(os.path.join(self.configDir, 'hotkeys.json'), {})
    
    @classmethod
    def new(cls, name : str, path : str):
        path = os.path.abspath(path)
        vault = ObsidianVault(name, path, sixteen_characters_hash(os.path.join(path, name)))
        if os.path.exists(vault.configDir):
            raise FileExistsError(f"Vault {name} already exists")

        vault.reset()
        return vault
    
    @classmethod
    def fromLocal(cls, path : str):
        path = os.path.abspath(path)
        base, name = split_path_at_last_separator(path, '\\')
        for k, v in obsidianApp.setting['vaults'].items():
            if v['path'] == path:
                return cls(name, base, k)
        
        return cls(name, base, sixteen_characters_hash(path))

    @classmethod
    def fromName(cls, name : str):
        for k, v in obsidianApp.setting['vaults'].items():
            base, name2 = split_path_at_last_separator(v['path'], '\\')
            if name == name2:
                return cls(name, base, k)
        
    def register(self):
        if self.uid in obsidianApp.setting['vaults']:
            return
        
        vault: VaultCtx = {
            "path" : self.vaultDir,
            "ts" : int(time.time()),
        }
        obsidianApp.setting['vaults'][self.uid] = vault
        obsidianApp.setting._save()

    def deregister(self):
        if self.uid not in obsidianApp.setting['vaults']:
            return
        
        for k, v in obsidianApp.setting['vaults'].items():
            if k == self.uid:
                del obsidianApp.setting['vaults'][k]
                obsidianApp.setting._save()
                break
            
        if os.path.exists(os.path.join(obsidianApp.roamingSettingPath, f"{self.uid}.json")):
            os.remove(os.path.join(obsidianApp.roamingSettingPath, f"{self.uid}.json"))
            
    def open(self):
        run_uri(f"obsidian://open?vault={self.uid}")
