
import subprocess
import platform
import hashlib


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
            
def sixteen_characters_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

def split_path_at_last_separator(path, separator):
    """
    Splits a path string based on the last occurrence of a specified separator.

    Parameters:
    path (str): The path string to be split.
    separator (str): The separator character or substring.

    Returns:
    tuple: A tuple containing the base path and the last part of the path.
    """
    last_index = path.rfind(separator)
    base_path = path[:last_index] if last_index != -1 else path
    last_part = path[last_index + 1:] if last_index != -1 else ''
    return base_path, last_part