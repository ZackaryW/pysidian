import logging
import os
import click
from pysidian.core import Plugin, Vault
from pysidian.utils import walk_to_target

pluginQuery : str = None
pluginObj : Plugin = None
runnedSeq : set = set()

@click.group("plugin", invoke_without_command=True, chain=True, help="plugin commands")
@click.option("--name", "-n", default=None, help="plugin name", type=click.STRING)
@click.option("--max-recurs-depth", "-d", default=2, help="max recursion depth", type=click.INT)
def cli_plugin(name, max_recurs_depth):
    if name is None:
        target = walk_to_target(".pysidian", os.getcwd(), max_recurs_depth)
        name = os.path.dirname(target)
        
    global pluginQuery, pluginObj
    pluginQuery = name
    click.echo(f"setting plugin dir to {pluginQuery}")
    pluginObj = Plugin.get(pluginQuery)

@cli_plugin.command("init", help="init plugin workplace")
@click.option("--workdir", "-w", default="src")
def cli_plugin_init(workdir):
    global pluginQuery, pluginObj
    if isinstance(pluginObj, Plugin):
        raise click.ClickException(f"Plugin {pluginQuery} already exists")
    else:
        pluginObj = Plugin.init(pluginQuery, workdir)

@cli_plugin.command("stage", help="stage plugin changes")
def cli_plugin_stage():
    global pluginObj, pluginQuery, runnedSeq
    try:
        runnedSeq.add("stage")

        if not pluginObj:
            raise click.ClickException(f"Plugin {pluginQuery} does not exist")
    
        pluginObj.stage()
        click.echo(f"Plugin {pluginQuery} staged")
    except Exception as e:
        raise click.ClickException(e.args[0])

@cli_plugin.command("commit", help="commit plugin changes")
@click.option("--no-stage", "-ns", is_flag=True, help="commit without stage")
@click.pass_context
def cli_plugin_commit(ctx : click.Context, no_stage):
    
    global pluginObj, pluginQuery, runnedSeq
    if not pluginObj:
        raise click.ClickException(f"Plugin {pluginQuery} does not exist")

    if "stage" not in runnedSeq and not no_stage:
        try:
            ctx.invoke(cli_plugin_stage)
        except Exception as e:
            if e.args[0] == "already staged":
                click.echo(f"Plugin {pluginObj.id} already staged")
            else:
                raise click.ClickException(e.args[0])

    runnedSeq.add("commit")

    try:
        pluginObj.commit()
        click.echo(f"Plugin {pluginQuery} committed")
    except Exception as e:
        click.echo(e.args[0])

@cli_plugin.command("push", help="push plugin changes")
@click.option("--no-stage", "-ns", is_flag=True, help="push without stage")
@click.option("--no-commit", "-nc", is_flag=True, help="push without commit")
@click.option("--version", "-v", default=None, help="version to push", type=click.STRING)
@click.pass_context
def cli_plugin_push(ctx : click.Context, no_stage, no_commit, version):
    global pluginObj, pluginQuery, runnedSeq
    if not pluginObj:
        raise click.ClickException(f"Plugin {pluginQuery} does not exist")

    if any(x not in runnedSeq for x in ["stage","commit"]) and not no_commit:
        try:
            ctx.invoke(cli_plugin_commit, no_stage=no_stage)
        except Exception as e:
            if e.args[0].startswith("already"):
                click.echo(f"Plugin {pluginObj.id} {e.args[0]}")
            else:
                raise click.ClickException(e.args[0])
    try:
        pluginObj.push(version)
    except Exception as e:
        raise click.ClickException(e.args[0])
    click.echo(f"Plugin {pluginObj.id} pushed")

@cli_plugin.command("open", help="open plugin work folders")
@click.option("--workdir", "-w", is_flag=True, help="open workdir")
@click.option("--cwd", "-c", is_flag=True, help="open cwd")
@click.option("--staging", "-s", is_flag=True, help="open staging folder")
def cli_plugin_open(workdir, cwd, staging):
    global pluginObj, pluginQuery
    if not pluginObj:
        raise click.ClickException(f"Plugin {pluginQuery} does not exist")
    if workdir:
        pluginObj.openWorkDir()
    elif cwd:
        pluginObj.openWorkplace()
    elif staging:
        pluginObj.openStagingDir()
    else:
        pluginObj.openWorkDir()

@cli_plugin.command("reg", help="register plugin as a update src for vault")
@click.option("--path", "-p", default=None, help="plugin path", type=click.STRING)
@click.option("--no-search-local", "-ns", is_flag=True, help="no search local")
def cli_plugin_reg(path, no_search_local):
    global pluginObj, pluginQuery
    if not pluginObj:
        raise click.ClickException(f"Plugin {pluginQuery} does not exist")
    
    if path is None and not no_search_local:
        raise click.ClickException("no path provided")
    
    if path is None:
        target = walk_to_target(".obsidian", os.getcwd(), 2)
        if target is None:
            raise click.ClickException("no obsidian folder found")
        else:
            path = os.path.dirname(target)
    
    try:
        vault = Vault.getVault(path)
        pluginObj.addVault(vault)
    except Exception as e:
        raise click.ClickException(e.args[0])
        
