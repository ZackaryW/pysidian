import click
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysidian.cli.plugin import cli_plugin
from pysidian.cli.vault import cli_vault

@click.group()
def cli():
    pass
    
cli.add_command(cli_plugin)
cli.add_command(cli_vault)

if __name__ == "__main__":
    cli()