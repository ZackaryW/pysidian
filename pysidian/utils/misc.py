import uuid
import os
import platform
import subprocess

def custom_uid(text : str):
    return uuid.uuid5(uuid.NAMESPACE_URL, text).hex[:16]

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
