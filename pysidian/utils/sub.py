import platform
import subprocess

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