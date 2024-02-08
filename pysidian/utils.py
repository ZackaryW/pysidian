
import typing
import toml
import os
import platform
import subprocess
import uuid
import orjson


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