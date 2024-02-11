# pysidian
A CLI tool written in Python intended for managing obsidian plugin deployments and development

## Installation
to install a safer version 
```bash
pip install pysidian
```

## Security Considerations
- Do not use PluginWorkplace.createFromSample() in production

## Example usage
```py
import shutil
import os
from pysidian import Plugin, Vault
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

p.openWorkDir()
```

