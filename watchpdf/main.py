""" Entry point to the watchpdf cli.  """
import typer
import warnings
import watchdog
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileCreatedEvent
import time
from pathlib import Path
import pdfrenamer
import pdf2bib
import pdf2doi
import pdfrenamer.config as config
from pdfrenamer.filename_creators import build_filename, AllowedTags, check_format_is_valid
import pdftitle

try
    import sci_rename
    SCI_RENAME_IMPORTED = True
except ImportError:
    SCI_RENAME_IMPORTED = False

from typing import Optional

from .utils import load_config_file, is_pdf, write_config, fix_filepath

app = typer.Typer()

# events are handled sequentially
recently_created_list = set([])

# we do not trust pdf2doi web search methods
pdf2doi.config.set('webvalidation',False)

def try_pdf2bib(config, file_src):
    new_file_name = None

    try:
        result = pdf2bib.pdf2bib_singlefile(str(file_src))

        if result['method'] == 'title_google':
            return None

        if result['metadata'] and result['identifier']:
            #closely following https://github.com/MicheleCotrufo/pdf-renamer/blob/master/pdfrenamer/main.py
            # however we want control as to when we actually rename the file 
            metadata = result['metadata'].copy()
            metadata_string = "\n\t"+"\n\t".join([f"{key} = \"{metadata[key]}\"" for key in metadata.keys()] ) 

            tags = check_format_is_valid(config['format'])
            new_file_name = build_filename( metadata, config['format'], tags)
        else:
            return None

    except Exception as e:
        print(f'error when processing {file_src}')
        print(e)
        return None

    return new_file_name

def try_pdftitle(config, file_src):
    try:
        with open(file_src, 'rb') as f: 
            title = pdftitle.get_title_from_io(f)

        return title

    except Exception as e:
        print(f'error when processing {file_src}')
        print(e)
        return None

def try_sci_rename(config, file_src):
    global SCI_RENAME_IMPORTED

    if not SCI_RENAME_IMPORTED:
        return None

    new_file_name = None
    try:
        new_file_name = sci_rename.search_candidate_title(str(file_src.parents[0]), file_src.name)

        if new_file_name is not None:
            # remove pdf ext
            new_file_name = Path(new_file_name).stem

    except Exception as e:
        print(f'error when processing {file_src}')
        print(e)
        return None

    return new_file_name

def get_new_filename(config, file_src) -> str:
    new_file_name = try_pdf2bib(config, file_src)

    if new_file_name is None:
        new_file_name = try_pdftitle(config, file_src)

    if new_file_name is None:
        new_file_name = try_sci_rename(config, file_src)

    return new_file_name


def update_file(config, file_src: Path):
    file_src = Path(file_src)

    if file_src in recently_created_list:
        recently_created_list.remove(file_src)
    else:
        new_file_name = get_new_filename(config, file_src)

        if new_file_name is not None:
            # if filename already matches then skip
            if new_file_name == Path(file_src).stem:
                pass
            else:
                pdfrenamer.main.rename_file(file_src, str(file_src.parents[0] / new_file_name), file_src.suffix)

            recently_created_list.add(new_file_name)

class NewFileEventHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        super(NewFileEventHandler, self).__init__()

    def on_any_event(self, event):
        if type(event) == FileCreatedEvent:
            file_src: Path = Path(event.src_path)

            if not is_pdf(file_src):
                return None

            file_src = str(file_src)
            update_file(self.config, file_src)

@app.command()
def watch(ctx: typer.Context):
    config = ctx.obj
    if len(config['watch_folder_list']) == 0:
        print('Nothing to watch!')
        # nothing to watch
        return 

    event_handler = NewFileEventHandler(config)

    obs_list = []
    for f in config['watch_folder_list']:
        observer = Observer()
        # TODO: add recursive as a config option
        observer.schedule(event_handler, f, recursive=True)
        obs_list.append(observer)

    for observer in obs_list:
        observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        for observer in obs_list:
            observer.stop()
            observer.join()

@app.command()
def add(ctx: typer.Context, watch_folder):
    """ Add a folder to the watch list """

    watch_folder = Path(watch_folder)
    # ensure a proper path and replace ~ with home dire
    watch_folder = str(fix_filepath(watch_folder))
    
    config: dict = load_config_file()

    # only add if not already watching
    if watch_folder not in config['watch_folder_list']:
        config['watch_folder_list'].append(watch_folder)

    write_config(config)

@app.command()
def clear_watch_folders(ctx: typer.Context):
    """ Delete all watch folders from config """
    config: dict = load_config_file()
    config['watch_folder_list'] = []
    write_config(config)

@app.command()
def scan(ctx: typer.Context, folder_path: Optional[str] = None):
    # update all pdfs in the watch folders
    config = ctx.obj
    if (len(config['watch_folder_list']) == 0) and (folder_path == None):
        print('Nothing to watch!')
        return 

    if folder_path is not None:
        folder_path = str(fix_filepath(Path(folder_path)))
        pdfrenamer.main.rename(folder_path, format=config['format'])
    else:
        for f in config['watch_folder_list']:
            pdfrenamer.main.rename(f, format=config['format'])

@app.callback()
def global_state(ctx: typer.Context, verbose: bool = False, dry: bool = False):
    """
    This function will be run before every cli function
    It sets up the current state and sets global settings.
    """

    config: dict = load_config_file()
    # store the config in the typer/click context that will be passed to all commands
    ctx.obj = config

def main():
    app()
