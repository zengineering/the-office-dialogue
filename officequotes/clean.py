import re
import click

context_regex = re.compile('\[.*?\]')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command('clean_data', context_settings=CONTEXT_SETTINGS)
@click.argument('filename', type=click.Path(exists=True))
def clean_data(filename):
    '''
    Cleanup data for analysis
    '''
    with open(filename, 'r') as f:
        for line in f:
            print(re.sub(context_regex, '', line), end='')


