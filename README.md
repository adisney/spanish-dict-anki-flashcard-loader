# SpanishDict Word of the Day Flashcard Loader
Load all new words from SpanishDict's [Word of the Day](https://www.spanishdict.com/wordoftheday) page. Any date that has previously been loaded will be skipped.

To avoid conflicts you will be prompted if a similar word is already present in your flashcard deck.

## Collection syncing
The script will attempt to sync your Anki collection prior to running the script. You must verify that syncinc was successful and notify the script to proceed.

The script will also sync the collection upon completion. If this sync fails you will be notified that you must proceed syncing manually to update the newest cards.

## Development setup

```sh
virtualenv .word-of-the-day
source .word-of-the-day/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
source .word-of-the-day/bin/activate
python main.py
```

## Anki

To load the data to your Anki profile, you will need to be running Anki's [Desktop](https://apps.ankiweb.net/) app and have the plugin [Anki Connect](https://foosoft.net/projects/anki-connect/) installed.

## Application installation

[pyinstaller](https://pyinstaller.org/en/stable/) is used to create a bundle that can be used to run these scripts without activating the venv and without running through the python interpreter.

`pyinstaller` creates the `dist/<entrypoint_file_name>` directory. This directory contains all the file dependencies (including whatever is needed to run the correct version of python) and a binary file of the name of the entry point file. The binary will error unless it is able to find all of the bundled files coincident with itself.

### Suggested install configuration

Copy the entire `dist/<entrypoint_file_name>` directory `/opt/python_dist`.
Create a symlink in `/opt/bin/<entrypoint_file_name>` that points to the dist.
Ensure `/opt/bin` is on your env path.

#### Word of the day
```sh
pyinstaller word_of_the_day.py
cp -r dist/word_of_the_day /opt/python_dist/
```

#### Translate word
```sh
pyinstaller translate_word.py
cp -r dist/translate_word /opt/python_dist/
```
