import os
from pysidian.core.plugin import ObsidianPlugin, testManifest
import click

from pysidian.core.vault import ObsidianVault
 
@click.group("plugin")
def plugin():
    pass

@plugin.command("mf")
@click.option("-p", "--path", default=os.getcwd(), help="Path to plugin")
@click.pass_context
def create_manifiest(ctx, path):
    p = ObsidianPlugin(path)
    p.manifest = testManifest
    ctx.obj["targetPlugin"] = p
    
@plugin.command("bkup") 
@click.argument("path")
@click.pass_context
def bkup(ctx, path):
    ctx.obj["targetPlugin"].bkup(path)

@plugin.command("load")
@click.pass_context
def update(ctx):
    p : ObsidianPlugin =ctx.obj["targetPlugin"]
    v : ObsidianVault = ctx.obj["targetVault"]
    p.update(v)
    