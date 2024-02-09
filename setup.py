import shutil
from setuptools import setup
from setuptools.command.install import install
import os
import pkg_resources
import base64

verifierBytes = b"""ZGVmIHZlcmlmaWVyKCk6CiAgICBpbXBvcnQgd2FybmluZ3MKICAgIGZyb20gcHlzaWRpYW4udXRp
bHMgaW1wb3J0IGNvbXB1dGVfaGFzaAogICAgaW1wb3J0IG9zCiAgICBjdXJyZW50RGlyID0gb3Mu
cGF0aC5kaXJuYW1lKG9zLnBhdGgucmVhbHBhdGgoX19maWxlX18pKQoKICAgIG9zc2V0ID0gc2V0
KAogICAgICAgIFt4LnNwbGl0KCIuIilbMF0gZm9yIHggaW4gb3MubGlzdGRpcihjdXJyZW50RGly
KSAKICAgICAgICBpZiBub3QgeC5zdGFydHN3aXRoKCJfIikgYW5kIHguZW5kc3dpdGgoIi56aXAi
KV0KICAgICkKICAgIGdsb2JhbHNldCA9IHNldChbeCBmb3IgeCBpbiBnbG9iYWxzKCkua2V5cygp
IGlmIG5vdCB4LnN0YXJ0c3dpdGgoIl8iKV0pCiAgICAKICAgIGlmIG9zc2V0IC0gZ2xvYmFsc2V0
OgogICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNrc3VtIE1pc21hdGNoLCBkYXRhIG1heSBiZSBj
b3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNrc3VtIE1p
c21hdGNoLCBkYXRhIG1heSBiZSBjb3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAgIHdhcm5p
bmdzLndhcm4oIkNoZWNrc3VtIE1pc21hdGNoLCBkYXRhIG1heSBiZSBjb3JydXB0ZWQgb3IgdGFt
cGVyZWQiKQogICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNrc3VtIE1pc21hdGNoLCBkYXRhIG1h
eSBiZSBjb3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNr
c3VtIE1pc21hdGNoLCBkYXRhIG1heSBiZSBjb3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAg
IHJldHVybgoKICAgIGZvciBuYW1lLCBoYXNoY29yZCBpbiBnbG9iYWxzKCkuaXRlbXMoKToKICAg
ICAgICBpZiBuYW1lLnN0YXJ0c3dpdGgoIl8iKToKICAgICAgICAgICAgY29udGludWUKCiAgICAg
ICAgaWYgbm90IGlzaW5zdGFuY2UoaGFzaGNvcmQsIHN0cik6CiAgICAgICAgICAgIGNvbnRpbnVl
CgogICAgICAgIGZpbGVwYXRoID0gb3MucGF0aC5qb2luKGN1cnJlbnREaXIsIGYie25hbWV9Lnpp
cCIpCiAgICAgICAgCiAgICAgICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKGZpbGVwYXRoKSBvciBj
b21wdXRlX2hhc2goZmlsZXBhdGgpICE9IGhhc2hjb3JkOiAKICAgICAgICAgICAgd2FybmluZ3Mu
d2FybigiQ2hlY2tzdW0gTWlzbWF0Y2gsIGRhdGEgbWF5IGJlIGNvcnJ1cHRlZCBvciB0YW1wZXJl
ZCIpCiAgICAgICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNrc3VtIE1pc21hdGNoLCBkYXRhIG1h
eSBiZSBjb3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAgICAgICB3YXJuaW5ncy53YXJuKCJD
aGVja3N1bSBNaXNtYXRjaCwgZGF0YSBtYXkgYmUgY29ycnVwdGVkIG9yIHRhbXBlcmVkIikKICAg
ICAgICAgICAgd2FybmluZ3Mud2FybigiQ2hlY2tzdW0gTWlzbWF0Y2gsIGRhdGEgbWF5IGJlIGNv
cnJ1cHRlZCBvciB0YW1wZXJlZCIpCiAgICAgICAgICAgIHdhcm5pbmdzLndhcm4oIkNoZWNrc3Vt
IE1pc21hdGNoLCBkYXRhIG1heSBiZSBjb3JydXB0ZWQgb3IgdGFtcGVyZWQiKQogICAgICAgICAg
ICByZXR1cm4KICAgICAKdmVyaWZpZXIoKQ=="""

verfier = base64.b64decode(verifierBytes).decode("utf-8")

def compute_hash(file_path, hash_algorithm="sha256"):
    import hashlib
    try:
        import platform
        import subprocess
        
        """Compute the hash of a file, using system utilities when available."""
        system = platform.system()
    except: # noqa
        system = None

    if system == "Windows":
        # Use CertUtil on Windows
        command = ['CertUtil', '-hashfile', file_path, hash_algorithm.upper()]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            # Output parsing may vary depending on the utility
            return result.stdout.splitlines()[1].strip()
    elif system in ["Linux", "Darwin"]:
        # Use shasum on Linux and macOS, adjusting parameters as necessary
        if hash_algorithm.lower() == "sha256":
            command = ['shasum', '-a', '256', file_path]
        else:
            # Default to SHA1 for simplicity in this example
            command = ['shasum', file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.split().pop(0)
    # Fallback to using hashlib if system-specific command isn't implemented
    hash_func = getattr(hashlib, hash_algorithm.lower(), None)
    if hash_func is None:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")
    with open(file_path, "rb") as f:
        file_hash = hash_func()
        while chunk := f.read(4096):
            file_hash.update(chunk)
        return file_hash.hexdigest()

class CustomInstallCommand(install):
    def run(self):
        # Running the standard install process
        install.run(self)

        package_path = os.path.join(self.install_lib, 'pysidian')
        print(f"Package installed at: {package_path}")

        #os.startfile(package_path)

        data_folder = os.path.join(package_path, "data")
        data_init = os.path.join(package_path, "data" ,'__init__.py')

        # delete all subfolders
        for f in os.listdir(data_folder):
            if os.path.isdir(os.path.join(data_folder, f)):
                shutil.rmtree(os.path.join(data_folder, f), ignore_errors=True)


        # write init file
        with open(data_init, "w") as fp:
            for f in os.listdir(data_folder):
                if not f.endswith(".zip"):
                    continue

                basename = os.path.basename(f).split(".")[0]
                fp.write(f"{basename} = '{compute_hash(os.path.join('pysidian/data', f))}'\n")

            fp.write("\n\n")

            fp.write(verfier)

        try:
            pkg_resources.get_distribution('pyarmor')
            print("PyArmor is installed.")
        except pkg_resources.DistributionNotFound:
            print("pyarmor not found, skipping pyarmor setup")
            print("user will be responsible for their own safety")

            return

        print("pyarmor found, generating data checksums")
    
        from pyarmor.cli.__main__ import main_entry
        main_entry(["gen", "-O",data_folder, data_init, "--restrict"])

if __name__ == "__main__":
    import sys
    if os.getenv('NO_ARMOR', 'false').lower() == 'true':
        extras = []
    else:
        extras = ['pyarmor']
    
    sys.argv.insert(1, "install")


setup(
    name="pysidian",
    version="3.1.0",
    packages=[
        "pysidian",
        "pysidian.core",
        "pysidian.cli",
        "pysidian.data",
    ],
    install_requires=[
        "click",
        "toml",
        "packaging",
        "psutil",
        "sioDict",
        "orjson",
        "uuid",
    ],
    # include zip files
    include_package_data=True,
    package_data={
        "pysidian.data": ["*.zip"],
    },
    entry_points={
        "console_scripts": [
            "pysidian = pysidian.cli.__main__:cli",
        ]
    },
    cmdclass={"install": CustomInstallCommand},
    python_requires=">=3.10",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ZackaryW",   
)
