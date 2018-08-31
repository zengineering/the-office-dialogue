import click

from .download import download, download_async
from .corrections import corrections

@click.group()
def cli():
    pass

cli.add_command(download)
cli.add_command(download_async)
cli.add_command(corrections)

cli()
