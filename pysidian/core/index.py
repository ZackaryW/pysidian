from sioDict import OrjsonSioDict
import os
import orjson

@staticmethod
def _save(d, path : str):
    with open(path, 'wb') as f:
        f.write(orjson.dumps(d, option=orjson.OPT_INDENT_2))
OrjsonSioDict._save = _save

system_appdata = os.getenv("APPDATA")

system_appdata_obsidian = os.path.join(system_appdata, "obsidian")

system_obsidian_settings_path = os.path.join(system_appdata_obsidian, 'obsidian.json')

system_obsidian_settings = OrjsonSioDict(system_obsidian_settings_path)

current_core_dir = os.path.dirname(os.path.realpath(__file__))

current_mod_dir = os.path.dirname(current_core_dir)

current_data_dir = os.path.join(current_mod_dir, 'data')

current_vault_index_path = os.path.join(current_mod_dir, 'vault_index.json')

_vault_index_file = OrjsonSioDict(current_vault_index_path)


if not _vault_index_file.get("vaults", None):
    _vault_index_file["vaults"] = {}
current_vault_index = _vault_index_file["vaults"]

for k, v in system_obsidian_settings.get("vaults", {}).items():
    if k not in current_vault_index:
        current_vault_index[k] = {
            "path" : v.get("path"),
            "ts" : v.get("ts")
        }

if not _vault_index_file.get("aliases", None):
    _vault_index_file["aliases"] = {}
current_vault_alias = _vault_index_file["aliases"]

current_plugin_index_path = os.path.join(current_mod_dir, 'plugin_index.json')

_plugin_index_file = OrjsonSioDict(current_plugin_index_path)

if not _plugin_index_file.get("plugins", None):
    _plugin_index_file["plugins"] = {}
current_plugin_index = _plugin_index_file["plugins"]

if not _plugin_index_file.get("aliases", None):
    _plugin_index_file["aliases"] = {}
current_plugin_alias = _plugin_index_file["aliases"]
