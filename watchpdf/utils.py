import pathlib
from pathlib import Path
import json

def is_pdf(file_src: Path) -> bool:
    pdf_suffixes = ['.pdf']

    if str(file_src.suffix).lower() in pdf_suffixes:
        return True

    return False

def fix_filepath(fp: Path) -> Path:
    return fp.expanduser().absolute()

def ensure_proper_config(config):
    if 'watch_folder_list' not in config.keys():
        config['watch_folder_list'] = []


    if 'format' not in config.keys():
        config["format"] = "{T} - {aAall} - {Jabbr} - {MM} - {YYYY}"

    return config

def get_config_path() -> Path:
    """ Loads the config file at ~/watchpdf/config.json. """
    # first ensure that the folder exists
    config_fp: Path = pathlib.Path.home() / '.watchpdf'
    config_fp.mkdir(exist_ok=True)

    # check if the config exists
    config_file_fp = config_fp / 'config.json'

    return config_file_fp
        
def write_config(config: dict) -> None:
    config_path: Path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f)

def read_config() -> dict:
    config_path: Path = get_config_path()

    with open(config_path, "r") as f:
        config = json.load(f)

    config = ensure_proper_config(config)

    return config

def load_config_file() -> dict:
    """ Load the config file and if it does not exist create a blank one.  """

    config_path: Path = get_config_path()

    if not config_path.exists():
        # create an empty one
        write_config({})

    return read_config()
        



