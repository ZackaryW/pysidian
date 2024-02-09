import os
import sys
current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(current_dir)
os.chdir(current_dir)

os.remove("pysidian/data/pyarmor_runtime_000000/pyarmor_runtime.pyd")
from pysidian.utils import compute_hash # noqa

print(os.getcwd())

lines = []
for f in os.listdir("pysidian\\data"):
    if not f.endswith(".zip"):
        continue

    basename = os.path.basename(f).split(".")[0]
    lines.append(f"{basename} = '{compute_hash(os.path.join('pysidian/data', f))}'\n")


verfier = """
def verifier():
    import warnings
    from pysidian.utils import compute_hash
    import os
    currentDir = os.path.dirname(os.path.realpath(__file__))

    osset = set([x.split(".")[0] for x in os.listdir(currentDir) if not x.startswith("_")])
    globalset = set([x for x in globals().keys() if not x.startswith("_")])
    
    if osset - globalset:
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        return

    for name, hashcord in globals().items():
        if name.startswith("_"):
            continue

        if not isinstance(hashcord, str):
            continue

        filepath = os.path.join(currentDir, f"{name}.zip")
        
        if not os.path.exists(filepath) or compute_hash(filepath) != hashcord: 
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            return
     
verifier()
"""

with open("pysidian/data/__init__.py", "w") as fp:
    fp.writelines(lines)
    fp.write("\n\n")
    fp.write(verfier)


print("generating pyarmor")
os.system("pyarmor gen --output pysidian/data/ pysidian/data/__init__.py")
# edit the 2nd line so that 
# from from pyarmor_runtime_000000 import __pyarmor__
# to from .pyarmor_runtime_000000 import __pyarmor__
with open("pysidian/data/__init__.py", "r") as fp:
    lines = fp.readlines()
    lines[1] = "from .pyarmor_runtime_000000 import __pyarmor__\n"
with open("pysidian/data/__init__.py", "w") as fp:
    fp.writelines(lines)

