import shutil
import click
import os
import zipfile
from pysidian.local_brat import gen_plugin_checksum, getPluginId, updatePlugin
from pysidian.utils import mod_dir
from pysidian.utils.dict import getJson, getToml, getVal, writeToml
from pysidian.utils.sub import run_uri
import json
from pysidian.vault_reg import custom_uid, new_vault, register_vault, unregister_vault_via_path, unregister_vault_via_uid

@click.group()
def cli():
    pass

@cli.command("test_init", help="uses obsidian sample plugin for test")
@click.option("--target", "-t", default=None, help="Target extraction directory")
@click.option("--just-plugin", "-jp", is_flag=True, help="only init test plugin")
@click.pass_context
def test_init(ctx : click.Context,target : str, just_plugin : bool):
    ccwd = os.getcwd()

    os.makedirs(os.path.join(ccwd, "pysidian-release"), exist_ok=True)

    with zipfile.ZipFile(os.path.join(mod_dir, "ob_sample.zip") , 'r') as zip_ref:
        if target is not None:
            os.makedirs(os.path.join(ccwd, target), exist_ok=True)
            zip_ref.extractall(os.path.join(ccwd, target))
        else:
            zip_ref.extractall(ccwd)
            
    os.makedirs(os.path.join(ccwd, "pysidian-release"), exist_ok=True)
    writeToml({"pysidian" : {"pluginDir" : "testp"}}, os.path.join(ccwd, "project.toml"))
    
    if just_plugin:
        return
    ctx.invoke(newvault, name="testv")
    ctx.invoke(commit)
    
@cli.command("init", help="init plugin workplace")
def init():
    os.makedirs(os.path.join(os.getcwd(), "pysidian-release"), exist_ok=True)
    writeToml({"pysidian" : {"pluginDir" : ""}}, os.path.join(os.getcwd(), "project.toml"))

@cli.command("update", help="update plugin")
@click.option("--vault", "-v", default=None, help="Vault path")
@click.option("--plugin", "-p", default=None, help="Plugin dir")
@click.option("--disable", "-d", is_flag=True, help="Disable plugin by default")
def update(vault : str, plugin : str, disable : bool):
    if vault is None and os.path.exists(os.path.join(os.getcwd(), ".obsidian")):
        vault = os.getcwd()
        
    if plugin is None and os.path.exists(os.path.join(os.getcwd(), "pysidian-release")):
        plugin = os.path.join(os.getcwd(), "pysidian-release")
    
    if vault is None:
        projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
        vault = getVal(projectCfg, "pysidian::vaultDir")

    if vault is None:
        return click.echo("Vault path not set")
    
    if plugin is None:
        projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
        plugin = getVal(projectCfg, "pysidian::pluginDir")
        
    if plugin is None:  
        return click.echo("Plugin dir not set")
    
    updatePlugin(vault, plugin)
    
    if not disable:
        pluginId = getPluginId(plugin)
        communityPlugins = getJson(os.path.join(vault, ".obsidian", "community-plugins.json"))
        if pluginId not in communityPlugins:
            communityPlugins.append(pluginId)
            with open(os.path.join(vault, ".obsidian", "community-plugins.json"), "w") as f:
                f.write(json.dumps(communityPlugins))

@cli.command("commit", help="commit changes")
def commit():
    projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
    pluginDir = getVal(projectCfg, "pysidian::pluginDir")
    
    if pluginDir == "":
        return click.echo("pluginDir not set")
    
    # find main.js, manifest.json, styles.css
    for file in os.listdir(pluginDir):
        if file in ["main.js", "manifest.json", "styles.css"]:
            shutil.copy(os.path.join(pluginDir, file), os.path.join(os.getcwd(), "pysidian-release", file))
    
    # hash for the three files
    with open(os.path.join(os.getcwd(), "pysidian-release", "localBrat"),"w") as f:
        f.write(gen_plugin_checksum(pluginDir))

@cli.group("vault")
def vault():
    pass

@vault.command("new", help="create new vault")
@click.argument("name")
@click.option("--target", "-t", default="", help="Target extraction directory")
@click.option("--no-reg", "-n", is_flag=True, help="Don't register the vault")
def newvault(name, target : str ="", no_reg : bool = False):
    click.echo("creating new vault at " + os.path.join(os.getcwd(), name))
    if target == "":
        fpath = new_vault(name)
    else:
        fpath = new_vault(name, target)
        
    if no_reg:
        return writeToml(
            {
                "pysidian" : {"vaultDir" : fpath, "vaultUid" : custom_uid(fpath)}
            }, 
            os.path.join(os.getcwd(), "project.toml")
        )
        
    uid = register_vault(fpath)
    writeToml({"pysidian" : {"vaultDir" : fpath, "vaultUid" : uid}}, os.path.join(os.getcwd(), "project.toml"))
    
@vault.command("open")
@click.option("--uid", "-u", default=None, help="Vault uid")
def openvault(uid : str):
    if uid is None:
        projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
        uid = getVal(projectCfg, "pysidian::vaultUid")
    
    if uid is None:
        return click.echo("Vault uid not set")
    
    run_uri(f"obsidian://open?vault={uid}")
    
@vault.command("reg")
@click.option("--path", "-p", default=None, help="Vault path")
def regvault(path : str):
    if path is None and os.path.exists(os.path.join(os.getcwd(), ".obsidian")):
        path = os.getcwd()
    
    if path is None:
        projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
        path = getVal(projectCfg, "pysidian::vaultDir")
    
    if path is None:
        return click.echo("Vault path not set")
    
    register_vault(path)
    
@vault.command("unreg")
@click.option("--path", "-p", default=None, help="Vault path")
@click.option("--uid", "-u", default=None, help="Vault uid")
def unregvault(path : str, uid : str):
    if path is None and os.path.exists(os.path.join(os.getcwd(), ".obsidian")):
        path = os.getcwd()
    
    if path is None and uid is None:
        projectCfg = getToml(os.path.join(os.getcwd(), "project.toml"))
        path = getVal(projectCfg, "pysidian::vaultDir")
        uid = getVal(projectCfg, "pysidian::vaultUid")
    
    if path is None and uid is None:
        return click.echo("missing vault path or uid")
    
    if path is not None:
        unregister_vault_via_path(path)
    else:
        unregister_vault_via_uid(uid)
    
def cli_main():
    cli()