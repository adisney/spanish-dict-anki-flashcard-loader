import re
import requests
import json
from termcolor import colored

import util


ANKI_URL = 'http://localhost:8765'
ANKI_DECK_NAME = 'Español'
ANKI_NOTE_MODEL = 'Foreign Vocabulary (and reversed cards)'


def strip_gender_prefix(spanish_word):
    return re.sub(r'^El ', '', re.sub(r'^La ', '', spanish_word))


def find_anki_notes(spanish_word):
    isolated_word = strip_gender_prefix(spanish_word)
    query = f'deck:{ANKI_DECK_NAME}' \
            + '(' \
            + f'vocab:*{isolated_word}*' \
            + f' or front:*{isolated_word}*' \
            + f' or definition:*{isolated_word}*' \
            + f' or back:*{isolated_word}*' \
            + ')'
    payload = {
        'action': 'findNotes',
        'params': {
            'query': query,
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
    response = requests.post(ANKI_URL, data=json.dumps({'action': "sync"}))

    if response.status_code != 200:
        raise Exception(f'Error syncing collection: {response.json().get("error")}')

    message = colored(
        'Refer to the Anki desktop app... did syncing complete successfully? (y/N): ',
        'yellow'
    )
    if not util.should_proceed_on_user_input(message):
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

    if util.should_proceed_on_user_input('Do you want to proceed? (y/N): '):
        # Send the request to AnkiConnect API
        req = {
            'action': "addNote",
            'params': {
                'note': note,
            }
        }
        response = requests.post(ANKI_URL, data=json.dumps(req))

        # Check the response status
        if response.status_code == 200:
            response_json = response.json()
            if response_json.__class__ == int:
                print(colored('Word added to Anki flashcards successfully.', 'cyan'))
            elif 'error' in response.json():
                print(f'{colored("Error adding word to Anki:", "light_red")} {response.json().get("error")}')
            else:
                print(colored(f'Unknown error adding word to Anki: {response_json}', "light_red"))
    else:
        print('Not adding word...')


