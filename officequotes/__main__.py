import click

from .download import download
from .corrections import corrections

@click.group()
def cli():
    print("The Office")

cli.add_command(download)
cli.add_command(corrections)

cli()
