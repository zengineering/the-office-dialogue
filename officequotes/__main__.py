import click

from .download import download
from .corrections import corrections
from .database import create_db
from .analysis import analyze

@click.group(name="OfficeQuotes")
def cli():
    pass

cli.add_command(download)
cli.add_command(corrections)
cli.add_command(create_db)
cli.add_command(analyze)

cli()
