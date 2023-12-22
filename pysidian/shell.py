import click
import os
import sys
import click_shell
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysidian.core.vault import ObsidianVault # noqa
from pysidian.core.plugin import ObsidianPlugin, testManifest # noqa

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
    

@cli.command("tmf", help="test plugin manifest")
@click.option("-p", "--path", default=os.getcwd(), help="Path to plugin")
@click.pass_context
def create_manifiest(ctx, path):
    p = ObsidianPlugin(path)
    p.manifest = testManifest
    ctx.obj["targetPlugin"] = p

@cli.command("bkupPlugin", help="backup plugin") 
@click.argument("path")
@click.pass_context
def bkup(ctx, path):
    ctx.obj["targetPlugin"].bkup(path)

@cli.command("loadPlugin")
@click.option("-p", "--path", default=os.getcwd(), help="Path to plugin")
@click.pass_context
def update(ctx, path):
    if "targetPlugin" not in ctx.obj:
        ctx.obj["targetPlugin"] = ObsidianPlugin(path)
    
    p : ObsidianPlugin =ctx.obj["targetPlugin"]
    v : ObsidianVault = ctx.obj["targetVault"]
    p.update(v)



@cli.command("newVault", help="create new vault")
@click.argument("name")
@click.option("-p", "--path", default=".", help="Path to vault")
@click.pass_context
def new(ctx : click.Context, name, path):
    ctx.obj["targetVault"] = ObsidianVault.new(name, path)

@cli.command("selectVault", help="select vault")
@click.argument("name")
@click.pass_context
def select(ctx : click.Context, name):
    if "/" in name or "\\" in name:
        ctx.obj["targetVault"] = ObsidianVault.fromLocal(name)
        return
    
    v = ObsidianVault.fromName(name)
    if v is not None:
        ctx.obj["targetVault"] = v
        return

    v = ObsidianVault.fromLocal(name)
    if v is not None:
        ctx.obj["targetVault"] = v
        return
    
    raise Exception(f"Vault {name} not found")
    
@cli.command("openVault")
@click.pass_context
def open(ctx):
    ctx.obj["targetVault"].register()
    ctx.obj["targetVault"].open()
    
def main():
    cli()

if __name__ == "__main__":
    cli()