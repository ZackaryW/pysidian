import click
import os
import sys
import click_shell
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pysidian.shell.plugin import plugin # noqa
from pysidian.shell.vault import vault # noqa

@click_shell.shell(
    "pysidian", 
    help="Pysidian dev toolkit", 
    invoke_without_command=True,
    chain=True
)
@click.pass_context
def cli(ctx : click.Context):
    print("Pysidian dev toolkit")
    ctx.ensure_object(dict)
    

cli : click.Group = cli
cli.add_command(plugin)
cli.add_command(vault)

def main():
    cli()

if __name__ == "__main__":
    cli()