from functools import cached_property
import os
import zipfile
from sioDict import OneLayerDict, OneLayerList
from pysidian.core.index import current_data_dir

default_core_plugins = [
  "file-explorer",
  "global-search",
  "switcher",
  "tag-pane",
  "templates",
  "command-palette",
  "editor-status",
  "word-count"
]

default_core_plugins_migration = {
  "file-explorer": True,
  "global-search": True,
  "switcher": True,
  "graph": False,
  "backlink": False,
  "canvas": False,
  "outgoing-link": False,
  "tag-pane": True,
  "properties": False,
  "page-preview": False,
  "daily-notes": False,
  "templates": True,
  "note-composer": False,
  "command-palette": True,
  "slash-command": False,
  "editor-status": True,
  "bookmarks": False,
  "markdown-importer": False,
  "zk-prefixer": False,
  "random-note": False,
  "outline": False,
  "word-count": True,
  "slides": False,
  "audio-recorder": False,
  "workspaces": False,
  "file-recovery": False,
  "publish": False,
  "sync": False
}

class VaultConfig:
    def __init__(self, path : str):
        if ".obsidian" not in path:
            raise Exception(f"{path} is not an Obsidian vault")
        
        if not os.path.isdir(path):
            raise Exception(f"{path} is not a directory")

        self.__path = path
        if len(os.listdir(path)) == 0:
            with zipfile.ZipFile(os.path.join(current_data_dir, "obsidian_template.zip"), 'r') as zipObj:
                zipObj.extractall(os.path.dirname(path))


    @cached_property
    def app(self):
        return OneLayerDict(os.path.join(self.__path, "app.json"))
    
    @cached_property
    def appearance(self):
        return OneLayerDict(os.path.join(self.__path, "appearance.json"), {"accentColor": ""})
    
    @cached_property
    def community_plugins(self):
        return OneLayerList(os.path.join(self.__path, "community-plugins.json"), default_core_plugins)
    
    @cached_property
    def core_plugins(self):
        return OneLayerList(os.path.join(self.__path, "core-plugins.json"), default_core_plugins)
    
    @cached_property
    def core_plugins_migration(self):
        return OneLayerDict(os.path.join(self.__path, "core-plugins-migration.json"), default_core_plugins_migration)
    
