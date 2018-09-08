import json
import click
from pathlib import Path
from tqdm import tqdm


def correctNamesInJson(json_file, name_corrections):
    with open(json_file, 'r+') as f:
        episode = json.load(f)
        for quote in episode['quotes']:
            quote['speaker'] = name_corrections.get(quote['speaker'],
                                                    quote['speaker'])
        f.seek(0)
        json.dump(episode, f, indent=4, ensure_ascii=False)
        f.truncate()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command('corrections', context_settings=CONTEXT_SETTINGS)
@click.argument('json_dir', type=click.Path(exists=True))
def corrections(json_dir):
    '''
    Make name corrections in JSON.

    read officequotes/resources/name_corrections.json and
    apply the corrections to all episode JSON files.

    JSON_DIR must be a directory of the same structure as the
    outupt of officequotes.download
    '''
    resources_root = Path(__file__).resolve().parent/"resources"
    with open(resources_root/"name_corrections.json") as f:
        name_corrections = json.load(f)

    json_path_root = Path(json_dir).resolve()
    json_files = list(json_path_root.glob('**/the-office-S*-E*.json'))

    for jf in tqdm(json_files):
        try:
            correctNamesInJson(jf, name_corrections)
        except Exception as e:
            print("Corrections failed on {}:\n{}".format(jf, e))

