import json
import os
from time import sleep
import psutil

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

def generate_default_vault(path : str):
    os.makedirs(os.path.join(path, ".obsidian"), exist_ok=True)
    target_path = os.path.join(path, ".obsidian")


    if len(os.listdir(target_path)) > 0:
        return

    with open(os.path.join(target_path, "app.json"), "w") as f:
        f.write("{}")

    #appearance
    with open(os.path.join(target_path, "appearance.json"), "w") as f:
        f.write('{"accentColor": ""}')
    
    #community-plugins
    with open(os.path.join(target_path, "community-plugins.json"), "w") as f:
        f.write('{"plugins": []}')

    #core-plugins
    with open(os.path.join(target_path, "core-plugins.json"), "w") as f:
        json.dump(default_core_plugins, f)

    #core-plugins-migration
    with open(os.path.join(target_path, "core-plugins-migration.json"), "w") as f:
        json.dump(default_core_plugins_migration, f)


def killObsidianProcess():
    for proc in psutil.process_iter():
        if proc.name() == "Obsidian.exe":
            proc.kill()
    sleep(0.2)