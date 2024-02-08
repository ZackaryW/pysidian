import shutil
import os
from pysidian.core.plugin import Plugin
from pysidian.core.vault import Vault
from pysidian.core.index import current_plugin_index

p = Plugin.sample("testing", "pluginSrc")
p._clearStagingFolder()
p.stage()
try:
    p.commit()
except Exception as e:
    print(e.args[0])

shutil.rmtree(os.path.join("testing", "sampleVault"), ignore_errors=True)
v = Vault.init("testing/sampleVault")

try:
    p.addVault(v)
except Exception as e:
    print(e.args[0])
assert v.id in current_plugin_index.get(p.cwd).get("installed")

p.push()

v.open()

