import click
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysidian.cli.plugin import cli_plugin, cli_plugin_push
import pysidian.cli.plugin as pplugin
from pysidian.cli.vault import cli_vault, cli_vault_open
from pysidian.utils import walk_to_target
from pysidian.core.plugin import Plugin

@click.group()
def cli():
    pass
    
cli.add_command(cli_plugin)
cli.add_command(cli_vault)

@cli.command("flow", help="a direct method to run commit and open vault at the same time")
@click.option("--no-stage", "-ns", is_flag=True, help="push without stage")
@click.option("--no-commit", "-nc", is_flag=True, help="push without commit")
@click.option("--version", "-v", default=None, help="version to push", type=click.STRING)
@click.pass_context
def _std_flow(ctx : click.Context, no_stage, no_commit, version):
    if pplugin.pluginObj is None:
        target = walk_to_target(".pysidian", os.getcwd(), 3)
        name = os.path.dirname(target)
        pplugin.pluginQuery = name
        pplugin.pluginObj = Plugin.get(pplugin.pluginQuery)
    ctx.invoke(cli_plugin_push, no_stage=no_stage, no_commit=no_commit, version=version)
    ctx.invoke(cli_vault)
    ctx.invoke(cli_vault_open)


if __name__ == "__main__":
    cli()