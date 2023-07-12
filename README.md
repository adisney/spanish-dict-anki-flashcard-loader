# SpanishDict Word of the Day Flashcard Loader
Load all new words from SpanishDict's [Word of the Day](https://www.spanishdict.com/wordoftheday) page. Any date that has previously been loaded will be skipped.

To avoid conflicts you will be prompted if a similar word is already present in your flashcard deck.

## Collection syncing
The script will attempt to sync your Anki collection prior to running the script. You must verify that syncinc was successful and notify the script to proceed.

The script will also sync the collection upon completion. If this sync fails you will be notified that you must proceed syncing manually to update the newest cards.

## Installation

```
virtualenv .word-of-the-day
source .word-of-the-day/bin/activate
pip install -r requirements.txt
```

## Usage

```
source .word-of-the-day/bin/activate
python main.py
```

## Anki

To load the data to your Anki profile, you will need to be running Anki's [Desktop](https://apps.ankiweb.net/) app and have the plugin [Anki Connect](https://foosoft.net/projects/anki-connect/) installed.
