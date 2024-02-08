import click

@click.group("plugin", invoke_without_command=True, chain=True)
@click.argument("name")
def cli_plugin(name):
    print(name)

@cli_plugin.command("init")
def cli_plugin_init():
    print("init")

@cli_plugin.command("stage")
def cli_plugin_stage():
    print("stage")

@cli_plugin.command("commit")
def cli_plugin_commit():
    print("commit")

@cli_plugin.command("push")
def cli_plugin_push():
    print("push")

