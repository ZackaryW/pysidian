_x1 = '224a09b94b6216227b2ad111d913a7579127dc6f8da2f85d0aeade851a2b7d42'
_x2 = '60f3dff35b0865e9ff160bf79017866477e49746ab95db542bff7a5c0dd0f06c'
import os #noqa

appdata = os.getenv("APPDATA")

obsidian_appdata = os.path.join(appdata, "obsidian")

obsidian_settings = os.path.join(obsidian_appdata, 'obsidian.json')

utils_dir = os.path.dirname(__file__)
mod_dir = os.path.dirname(utils_dir)

# check tampering
def tamper_check():
    import hashlib
    
    # sha256 check
    x1 = hashlib.sha256(open(os.path.join(mod_dir, 'ob_sample.zip'), 'rb').read()).hexdigest()
    x2 = hashlib.sha256(open(os.path.join(mod_dir, 'obsidian_template.zip'), 'rb').read()).hexdigest()

    if x1 == _x1 and x2 == _x2:
        return True
    else:
        return False

if not tamper_check():
    raise Exception("Tamper check failed")
