import click

@click.group("vault", invoke_without_command=True, chain=True)
@click.argument("name")
def cli_vault(name):
    print(name)

@cli_vault.command("init")
@click.option("--reset", "-r", is_flag=True)
def cli_vault_init(reset):
    print("init")

@cli_vault.command("open")
def cli_vault_open():
    print("open")

@cli_vault.command("reg")
def cli_vault_reg():
    print("reg")


