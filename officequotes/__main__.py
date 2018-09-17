import click

from .download import download
from .corrections import corrections
from .database import create_db
from .analysis import main_characters, analyze_character

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(name="officequotes", context_settings=CONTEXT_SETTINGS)
def top_cli(name="officequotes"):
    pass

top_cli.add_command(download)
top_cli.add_command(corrections)
top_cli.add_command(create_db)
top_cli.add_command(main_characters)
top_cli.add_command(analyze_character)

top_cli()
