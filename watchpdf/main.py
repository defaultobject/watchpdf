""" Entry point to the watchpdf cli.  """
import typer
import warnings
import watchdog
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileCreatedEvent
import time
from pathlib import Path
import pdfrenamer
from typing import Optional

from .utils import load_config_file, is_pdf, write_config, fix_filepath

app = typer.Typer()

# events are handled sequentially
recently_created_list = set([])

def update_file(config, file_src: Path):
    if file_src in recently_created_list:
        recently_created_list.remove(file_src)
    else:
        result = pdfrenamer.main.rename(str(file_src), format=config['format'])
        new_file_name = result['path_new']
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
