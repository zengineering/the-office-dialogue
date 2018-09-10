import click

from .download import download
from .corrections import corrections
from .database import create_db
from .analysis import line_counts

@click.group(name="officequotes")
def top_cli(name="officequotes"):
    pass

top_cli.add_command(download)
top_cli.add_command(corrections)
top_cli.add_command(create_db)
top_cli.add_command(line_counts)

top_cli()
