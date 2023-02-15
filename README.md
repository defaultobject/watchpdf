# watchpdf

`watchpdf` is a simple python cli to watch a folder and automatically rename academic pdf papers that get added. This is built using the following excellent tools:

- `watchdog` - https://github.com/gorakhargosh/watchdog

- `pdfrenamers` - [[GitHub - MicheleCotrufo/pdf-renamer: A python tool to automatically rename the pdf files of scientific publications by looking up the publication metadata on the web.](https://github.com/MicheleCotrufo/pdf-renamer)](https://github.com/MicheleCotrufo/pdf-renamer)



## Installation

install locally using `pip install -e .`  or through pip

```
pip install watchpdf
```

## Usage

First set a folder to watch

```bash
watchpdf add <path to folder>
```

You can add multiple folders, and `watchpdf` will watch them all. Simply call the `add` commands multiple times. This will create a config file in `~/.watchpdf/config.json`.

To start watching call

```bash
watchpdf watch
```

## Additional

To clear all watch folders call

```
watchpdf clear-watch-folders
```

`watchpdf` will only update new papers that are added when `watchpdf` is watching. To update all watched folders call

```
watchpdf scan
```

or to scan a specific folder

```
watchpdf scan <path_to_folder>
```

## Notes

`watchpdf` is very simply implemented and is only intended to have one instance of `watchpdf` running.
