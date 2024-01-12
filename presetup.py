import os
import hashlib

ob_sample_zip = os.path.join("pysidian", "ob_sample.zip")
obsidian_template_zip = os.path.join("pysidian", "obsidian_template.zip")

ob_hash = hashlib.sha256(open(ob_sample_zip, 'rb').read()).hexdigest()
ot_hash = hashlib.sha256(open(obsidian_template_zip, 'rb').read()).hexdigest()
print(f"hash for {ob_sample_zip} is {ob_hash}")
print(f"hash for {obsidian_template_zip} is {ot_hash}")

init_file = os.path.join("pysidian", "utils", "__init__.py")
with open(init_file, "r") as f:
    lines  = f.readlines()
with open(init_file, "w") as f:
    lines[0] = "_x1 = '" + ob_hash + "'\n"
    lines[1] = "_x2 = '" + ot_hash + "'\n"
    f.writelines(lines)
    
init_hash = hashlib.sha256(open(init_file, 'rb').read()).hexdigest()
    
print(f"hash for {init_file} is {init_hash}")

with open(os.path.join("pysidian", "cli.py"), "r") as f:
    lines  = f.readlines()
with open(os.path.join("pysidian", "cli.py"), "w") as f:
    lines[0] = 'record_hash = "' + init_hash + '"\n'
    f.writelines(lines)

print("done")
