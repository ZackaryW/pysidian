import os
import sys
current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(current_dir)
os.chdir(current_dir)
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

    for name, hashcord in globals().items():
        if name.startswith("_"):
            continue

        filepath = os.path.join(currentDir, f"{name}.zip")

        if not os.path.exists(filepath):
            continue

        if compute_hash(filepath) != hashcord:
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            return

"""

with open("pysidian/data/__init__.py", "w") as fp:
    fp.writelines(lines)
    fp.write("\n\n")
    fp.write(verfier)

os.system("pyarmor gen --output pysidian/data/ pysidian/data/__init__.py")
# edit the 2nd line so that 
# from from pyarmor_runtime_000000 import __pyarmor__
# to from .pyarmor_runtime_000000 import __pyarmor__
with open("pysidian/data/__init__.py", "r") as fp:
    lines = fp.readlines()
    lines[1] = "from .pyarmor_runtime_000000 import __pyarmor__\n"
with open("pysidian/data/__init__.py", "w") as fp:
    fp.writelines(lines)

