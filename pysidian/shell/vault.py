import click
from pysidian.core.vault import ObsidianVault
 
@click.group("vault")
def vault():
    pass

@vault.command("new")
@click.argument("name")
@click.option("-p", "--path", default=".", help="Path to vault")
@click.pass_context
def new(ctx : click.Context, name, path):
    ctx.obj["targetVault"] = ObsidianVault.new(name, path)

@vault.command("select")
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
    
@vault.command("open")
@click.pass_context
def open(ctx):
    ctx.obj["targetVault"].register()
    ctx.obj["targetVault"].open()
    