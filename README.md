# pysidian
A CLI tool written in Python intended for managing obsidian plugin deployments and development

## Installation
to install a safer version 
```py
# ensure pyarmor
pip install pyarmor
git clone https://github.com/ZackaryW/pysidian.git
cd pysidian
python setup.py install
```

```bash
pip install pysidian
```
## Cli Commands
|Command|Short|Description|
|--|--|--|
|flow |     |  a direct method to run commit and open vault at the same time|
|plugin|    |  plugin commands|
| | commit | commit plugin changes|
| | init  |  init plugin workplace|
| | open  |  open plugin work folders|
| | push  |  push plugin changes|
| | reg   |  register plugin as a update src for vault|
| | stage |  stage plugin changes|
vault |    |  vault commands|
| | init  |  init vault|
| | open  |  open vault|
| | reg   |  register vault|

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

# Acknowledgements
- uses pyarmor to obfuscate integrity check