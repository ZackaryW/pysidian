import typing
import click
import os
import sys

from pysidian.utils.misc import walk_to_target
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pysidian import Vault, PluginWorkplace
from pysidian.core.vault import vault_alias


@click.group(invoke_without_command=True)
@click.option("--version", "-v", help="get version", is_flag=True)
def cli(version):
    if version:
        click.echo("pysidian: " + "3.2.0")


@cli.group("vault", invoke_without_command=True, chain=True)
@click.option("--path", "-p", type=click.Path(exists=True), required=False, help="Vault path")
@click.option("--id", "-i", required=False, help="Vault ID")
@click.option("--alias", "-a", required=False, help="Vault alias")
@click.pass_context
def vault(ctx : click.Context, path : str, id : str, alias : str): 
    if not path and not id and not alias:
        res = walk_to_target(".obsidian", os.getcwd(), 3)
        if res is not None:
            path = os.path.dirname(res)
            ctx.obj = Vault(path)
            click.echo("Opened " + path)
    elif (res := Vault.fetch(alias, path, id)):
        ctx.obj = res
        click.echo("Opened " + res.path)
    else:
        click.echo("No Vault Selected")
        

@vault.command("open")
@click.pass_obj
def _vault_open(obj : Vault): 
    if obj is None:
        return click.echo("Open Vault command failed, no vault selected")

    obj.open()

@vault.command("create")
@click.argument("path")
@click.pass_context
def _vault_create(ctx : click.Context, path : str):
    ctx.obj = Vault(path)
    click.echo("Created Vault " + path)

@vault.command("reg")
@click.option("--obsidian-index", "-o", is_flag=True, help="add to obsidian index")
@click.pass_obj
def _vault_reg(obj : Vault, obsidian_index : bool):
    if obj is None:
        return click.echo("Register Vault command failed, no vault selected")

    if obsidian_index and not obj.obsidianIndexed:
        obj.obsidianIndexed = True
    elif not obj.indexed:
        obj.indexed = True

    click.echo(f"Registered for {obj.path} at {'obsidian' if obj.obsidianIndexed else 'pysidian'}")

@vault.command("unreg")
@click.option("--obsidian-index", "-o", is_flag=True, help="remove from obsidian index")
@click.pass_obj
def _vault_unreg(obj : Vault, obsidian_index : bool):
    if obj is None:
        return click.echo("Unregister Vault command failed, no vault selected")

    if obsidian_index and obj.obsidianIndexed:
        obj.obsidianIndexed = False
    elif obj.indexed:
        obj.indexed = False

    click.echo(f"Unregistered for {obj.path} at {'obsidian' if obj.obsidianIndexed else 'pysidian'}")

@vault.command("alias")
@click.option("--edit-in-vscode", "-e", is_flag=True, help="edit in vscode")
@click.option("--name", "-n", help="set alias", multiple=True)
@click.option("--unset", "-u", is_flag=True, help="unset alias")
@click.pass_obj
def _vault_alias(obj : Vault, edit_in_vscode : bool, name : typing.List[str], unset : bool):
    if obj is None:
        return click.echo("Alias Vault command failed, no vault selected")

    if edit_in_vscode:
        os.system(f"code {vault_alias.filename}")
    elif name:
        obj.alias = obj.alias + name
    elif unset:
        obj.alias = list(set(obj.alias) - set(name))

@cli.group("plugin", invoke_without_command=True, chain=True)
@click.option("--path", "-p", type=click.Path(exists=True), required=False, help="Plugin path")
@click.pass_context
def plugin(ctx : click.Context, path : str): 
    w = PluginWorkplace.get(path)
    if w is None:
        return click.echo("Open Plugin command failed, no plugin selected")
    
    ctx.obj = w
    click.echo(f"Selected Plugin Workplace {w.path}")

@plugin.command("create")
@click.option("--path", "-p", type=click.Path(exists=True), required=False, help="Plugin path")
@click.option("--sample", "-s", is_flag=True, help="create sample plugin")
@click.pass_context
def _plugin_create(ctx : click.Context, path : str, sample : bool):
    if sample:
        w = PluginWorkplace.createFromSample(path)
    else:
        w = PluginWorkplace.create(path)
    if w is None:
        return click.echo("Create Plugin command failed, no plugin selected")
    
    ctx.obj = w
    click.echo(f"Created Plugin Workplace {w.path}")

@plugin.command("open")
@click.pass_obj
def _plugin_open(obj : PluginWorkplace):
    if obj is None:
        return click.echo("Open Plugin command failed, no plugin selected")

    obj.openFolder()

@plugin.command("reg")
@click.option("--unset", "-u", is_flag=True)
@click.pass_obj
def _plugin_reg(obj : PluginWorkplace, unset : bool):
    if obj is None:
        return click.echo("Register Plugin command failed, no plugin selected")

    if unset:
        obj.unsetGlobal()
        click.echo(f"Unregistered {obj.path}")
    else:
        obj.setGlobal()
        click.echo(f"Registered {obj.path}")

@plugin.command("index")
@click.pass_obj
def _plugin_index(obj : PluginWorkplace):
    if obj is None:
        return click.echo("Index Plugin command failed, no plugin selected")

    click.echo(obj.config.indexIntel)

@plugin.command("stage")
@click.pass_obj
def _plugin_stage(obj : PluginWorkplace):
    if obj is None:
        return click.echo("Stage Plugin command failed, no plugin selected")

    obj.stage()

@plugin.command("commit")
@click.pass_obj
def _plugin_commit(obj : PluginWorkplace):
    if obj is None:
        return click.echo("Commit Plugin command failed, no plugin selected")

    obj.commit()

@plugin.command("push")
@click.option("--version", "-v", help="set version")
@click.pass_obj
def _plugin_push(obj : PluginWorkplace, version : str):
    if obj is None:
        return click.echo("Push Plugin command failed, no plugin selected")

    try:
        obj.push(version)
        click.echo(f"Pushed {obj.path} at version {version or 'latest'}")
    except ValueError as e:
        return click.echo(e.args[0])

@plugin.command("auto")
@click.option("--alias", "-a", help="set alias")
@click.option("--testvault", "-t", help="create a test vault if one is absent", is_flag=True)
@click.option("--id", "-i", help="set id")
@click.option("--path", "-p", type=click.Path(exists=True), required=False, help="Plugin path")
@click.option("--index", "-x", type=int, required=False, help="Plugin index")
@click.pass_context
def _plugin_auto(ctx : click.Context, alias : str, id : str, path : str, index : int, testvault : bool):
    if ctx.obj is None:
        return click.echo("Auto Plugin command failed, no plugin selected")
    
    ctx.invoke(_plugin_stage)
    ctx.invoke(_plugin_commit)
    ctx.invoke(_plugin_push)
    
    wp : PluginWorkplace = ctx.obj

    if len(wp.config.testVaults) == 0:
        if not testvault:
            return click.echo("no test vault")
        else:
            wp.addLocalTestVault("vault-test")
    
    if path or id or alias:
        for vault in wp.config.testVaults:
            if vault.id == id  or vault.path == path or alias in vault.alias:
                vault.open()
                break
    elif index:
        wp.config.testVaults[index].open()
    else:
        wp.config.testVaults[0].open()
    


if __name__ == "__main__":
    cli()
