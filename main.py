from termcolor import colored
import time
import re
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from collections import namedtuple

ANKI_URL = 'http://localhost:8765'
ANKI_DECK_NAME = 'Español'
ANKI_NOTE_MODEL = 'Foreign Vocabulary (and reversed cards)'

WORD_OF_THE_DAY_URL = 'https://www.spanishdict.com/wordoftheday'
WORD_DIV_CLASS = 'IvPSNgXy'
MONTH_CLASS = 'jkQASa0U'
DATE_CLASS = 'Pu6E7CK7'
SPANISH_WORD_CLASS = 'tds4TDh9'
ENGLISH_WORD_CLASS = 'W9SgI1ND'
EXAMPLE_PHRASE_CLASS = 'xiQBRZra'
PHRASE_TRANSLATION_CLASS = 'KkXPxEB8'

# *****************
# General utilities
# *****************

Word = namedtuple("Word", ["date", "spanish", "english", "example", "translation"])


def should_proceed_on_user_input(message):
    user_input = input(message)
    return user_input.lower() == "y" or user_input.lower() == "Y"


def loadDateCache():
    cache = set()
    try:
        with open('.data/date_cache.txt', 'r') as dateCacheFile:
            for line in dateCacheFile.readlines():
                cache.add(line.strip())
    except FileNotFoundError:
        pass

    return cache


def updateCache(cache):
    with open('.data/date_cache.txt', 'w') as dateCacheFile:
        for date in sorted(cache):
            dateCacheFile.write(f'{date}\n')


def filler_progress_bar():
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")


def strip_gender_prefix(spanish_word):
    return re.sub(r'^El ', '', re.sub(r'^La ', '', spanish_word))


# **************
# Anki utilities
# **************


def find_anki_notes(spanish_word):
    isolated_word = strip_gender_prefix(spanish_word)
    payload = {
        'action': 'findNotes',
        'params': {
            'query': f'deck:{ANKI_DECK_NAME} (vocab:*{isolated_word}* or front:*{isolated_word}* or definition:*{isolated_word}* or back:*{isolated_word}*)'
        }
    }
    response = requests.post(ANKI_URL, data=json.dumps(payload))

    if response.status_code != 200:
        raise Exception('Failure searching for Anki notes')
    elif 'error' in response.json():
        raise Exception(f'Error in the query to find Anki notes for {spanish_word}')

    return response.json()


def find_anki_note_details(note_ids):
    payload = {
        'action': 'notesInfo',
        'params': {
            'notes': note_ids
        }
    }

    response = requests.post(ANKI_URL, data=json.dumps(payload))
    if response.status_code != 200:
        raise Exception('Failure searching for note details')
    elif 'error' in response.json():
        raise Exception(f'Error finding the notes details {response.json().get("error")}')

    return response.json()


def word_already_in_deck(notes):
    if notes:
        return True
    else:
        return False


def sync_anki_collection():
    print('Syncing collection')
    response = requests.post('http://localhost:8765/', data=json.dumps({'action': "sync"}))

    # Check the response status
    if response.status_code != 200:
        raise Exception(f'Error syncing collection: {response.json().get("error")}')

    if not should_proceed_on_user_input(colored('Refer to the Anki desktop app... did syncing complete successfully? (y/N): ', 'yellow')):
        raise Exception('Failed to sync collection')


def add_word_to_anki(word):
    print()

    note = {
        'deckName': ANKI_DECK_NAME,
        'modelName': ANKI_NOTE_MODEL,
        'fields': {
            'Vocab': word.spanish,
            'Definition': word.english,
            'Example Phrase': word.example,
            'Phrase Translation': word.translation,
        },
        'options': {
            'allowDuplicate': False
        }
    }
    print(colored('Adding the following note to Anki:', 'yellow'))
    print(json.dumps(note, indent=4, ensure_ascii=False))
    print()

    if should_proceed_on_user_input('Do you want to proceed? (y/N): '):
        # Send the request to AnkiConnect API
        req = {
            'action': "addNote",
            'params': {
                'note': note,
            }
        }
        response = requests.post('http://localhost:8765/', data=json.dumps(req))

        # Check the response status
        if response.status_code == 200:
            response_json = response.json()
            if response_json.__class__ == int:
                print(colored('Word added to Anki flashcards successfully.', 'cyan'))
            elif 'error' in response.json():
                print(f'Error adding word to Anki: {response.json().get("error")}')
            else:
                print(f'Unknown error adding word to Anki: {response_json}')
    else:
        print('Not adding word...')


# *****************
# SpanishDict utils
# *****************


def get_current_words():
    words = []
    current_year = str(datetime.now().year)

    response = requests.get(WORD_OF_THE_DAY_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    word_divs = soup.find_all('div', {'class': WORD_DIV_CLASS})

    for div in word_divs:
        month = div.find('div', {'class': MONTH_CLASS}).text
        day = div.find('div', {'class': DATE_CLASS}).text
        word_date = f'{current_year}-{month}-{day}'
        spanish_word = div.find('a', {'class': SPANISH_WORD_CLASS}).text.capitalize()
        english_word = div.find('div', {'class': ENGLISH_WORD_CLASS}).text.capitalize()
        example_phrase = div.find('div', {'class': EXAMPLE_PHRASE_CLASS}).text
        phrase_translation = div.find('div', {'class': PHRASE_TRANSLATION_CLASS}).text

        words.append(Word(word_date, spanish_word, english_word, example_phrase, phrase_translation))

    return words


# ****
# Main
# ****


def main():
    sync_anki_collection()
    filler_progress_bar()

    cache = loadDateCache()

    print('Getting all the currently available words')
    filler_progress_bar()

    for word in get_current_words():
        if word.date in cache:
            print(f'Word from {word.date} already in cache. Moving to next one.')
        else:
            cache.add(word.date)

            print(f'Found candidate: {colored(word.spanish, "green")} - {word.english}')

            notes = find_anki_notes(word.spanish)
            if not word_already_in_deck(notes):
                print('No conflicts found')
                add_word_to_anki(word)
            else:

                if notes:
                    details = find_anki_note_details(notes)

                    print()
                    print(colored(f'Potential conflicts for {word.spanish}:', "light_red"))
                    for detail in details:
                        print(f'\t{colored("Conflict", "light_red")}:')
                        for key, value in detail.get('fields').items():
                            print(f'\t\t{key}: {value.get("value")}')

                print()
                if should_proceed_on_user_input(f'Do you want to continue adding the word {colored(word.spanish, "green")}? (y/N): '):
                    add_word_to_anki(word)
                else:
                    print('Skipping...')

        filler_progress_bar()

    try:
        sync_anki_collection()
    except Exception:
        print(colored('Failed syncing the collection during cleanup. Must manually sync collection', 'light_red'))

    updateCache(cache)
    print()
    print(colored("All done! Study hard!", "yellow"))


print(colored("Let's add some new words to your flash cards!", "yellow"))
filler_progress_bar()

main()
