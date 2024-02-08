import click

from pysidian.core.vault import Vault
from pysidian.utils import walk_to_target
import os

vaultQuery : str = None
vaultObj : Vault = None

@click.group("vault", invoke_without_command=True, chain=True, help="vault commands")
@click.option("--name", "-n", default=None, help="vault name", type=click.STRING)
@click.option("--max-recurs-depth", "-d", default=2, help="max recursion depth", type=click.INT)
def cli_vault(name, max_recurs_depth):
    if name is None:
        target = walk_to_target(".obsidian", os.getcwd(), max_recurs_depth)
        name = os.path.dirname(target)
    
    if name is None:
        raise click.ClickException("Vault not found")

    global vaultQuery, vaultObj
    vaultQuery = name
    click.echo(f"setting vault dir to {vaultQuery}")
    vaultObj = Vault.getVault(vaultQuery)

@cli_vault.command("init", help="init vault")
@click.option("--reset", "-r", is_flag=True)
@click.option("--dont-keep-content", "-dkc", is_flag=True, help="reset keep content")
def cli_vault_init(reset, dont_keep_content):
    global vaultQuery, vaultObj
    if vaultObj is not None and not reset:
        pass
    elif vaultObj and reset:
        vaultObj.reset(not dont_keep_content)
    else:
        vaultObj = Vault.init(vaultQuery)


@cli_vault.command("open", help="open vault")
def cli_vault_open():
    if not vaultObj:
        raise click.ClickException("Vault not found")
    vaultObj.open()

@cli_vault.command("reg", help="register vault")
@click.option("--unregister", "-u", is_flag=True)
def cli_vault_reg(unregister):
    if not vaultObj:
        raise click.ClickException("Vault not found")
    if unregister:
        vaultObj.unreg()
    else:
        vaultObj.reg()



