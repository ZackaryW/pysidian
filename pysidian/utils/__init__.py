import os

appdata = os.getenv("APPDATA")

obsidian_appdata = os.path.join(appdata, "obsidian")

obsidian_settings = os.path.join(obsidian_appdata, 'obsidian.json')

utils_dir = os.path.dirname(__file__)
mod_dir = os.path.dirname(utils_dir)

