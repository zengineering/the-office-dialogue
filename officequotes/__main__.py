import click

from .download import download

@click.group()
def cli():
    print("The Office")

cli.add_command(download)

cli()
