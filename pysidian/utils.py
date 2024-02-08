
import typing
import toml
import os
import platform
import subprocess
import uuid
import orjson
import hashlib

def custom_uid(text : str):
    return uuid.uuid5(uuid.NAMESPACE_URL, text).hex[:16]

def exec(command : str, *args):
    """
    Executes a command with the given arguments.

    Args:
        command (str): The command to be executed.
        *args (tuple): Additional arguments for the command.
    """
    subprocess.Popen( # noqa
        [command] + list(args),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=
            subprocess.DETACHED_PROCESS |
            subprocess.CREATE_NEW_PROCESS_GROUP | 
            subprocess.CREATE_BREAKAWAY_FROM_JOB
    )

def run_uri(*args):
    match platform.system():
        case "Windows":
            exec("cmd", "/c", "start", *args)
        case "Linux":
            exec("xdg-open", *args)
        case "Darwin":
            exec("open", *args)

def touch_file(
    path : str, 
    type_ : typing.Literal["json", "toml", "misc"] = "json", 
    content : object = None,
    skip_if_exists : bool = True
):
    if type_ not in ("json", "toml", "misc"):
        type_ = "misc"

    if skip_if_exists and os.path.exists(path):
        return

    match (type_, content):
        case "misc", _:
            with open(path, "w") as f:
                f.write(str(content))
        case "json", dict() | list():
            with open(path, "w") as f:
                f.write(orjson.dumps(content))
        case "toml", dict():
            with open(path, "w") as f:
                toml.dump(content, f)
        case "json", None:
            with open(path, "w") as f:
                f.write(orjson.dumps({}))
        case "toml", None:
            with open(path, "w") as f:
                f.write("")
        case _:
            raise Exception("invalid type")

def load_json(path : str):
    with open(path, "rb") as f:
        return orjson.loads(f.read())
    
def save_json(path : str, d):
    with open(path, 'w') as f:
        f.write(orjson.dumps(d, option=orjson.OPT_INDENT_2))

def walk_to_target(target_file : str, path : str, max_depth : int):
    sources = os.listdir(path)
    #sort by most subfiles content
    sources.sort(key=lambda x: os.stat(os.path.join(path, x)).st_size, reverse=True)

    for file in sources:
        file_path = os.path.join(path, file)
        if file == target_file:
            return file_path
        elif os.path.isdir(file_path) and max_depth > 0:
            result = walk_to_target(target_file, file_path, max_depth - 1)
            if result:
                return result
            
    return None

def compute_hash(file_path, hash_algorithm="sha256"):
    """Compute the hash of a file, using system utilities when available."""
    system = platform.system()

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