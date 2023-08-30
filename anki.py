import requests
import json


ANKI_URL = 'http://localhost:8765'
ANKI_DECK_NAME = 'Español'
ANKI_NOTE_MODEL = 'Foreign Vocabulary (and reversed cards)'


def find_anki_notes(word):
    query = f'deck:{ANKI_DECK_NAME}' \
            + '(' \
            + f'vocab:*{word}*' \
            + f' or front:*{word}*' \
            + f' or definition:*{word}*' \
            + f' or back:*{word}*' \
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
        raise Exception(f'Error in the query to find Anki notes for {word}')

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
    response = requests.post(ANKI_URL, data=json.dumps({'action': "sync"}))

    if response.status_code != 200:
        raise Exception(f'Error syncing collection: {response.json().get("error")}')


def build_note(word):
    return {
        'deckName': ANKI_DECK_NAME,
        'modelName': ANKI_NOTE_MODEL,
        'fields': {
            'Vocab': word.spanish.capitalize(),
            'Definition': word.english.capitalize(),
            'Example Phrase': word.example,
            'Phrase Translation': word.translation,
        },
        'options': {
            'allowDuplicate': False
        }
    }


def add_note_to_collection(note):
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
            return {'success': True}
        elif 'error' in response.json():
            return {'success': False, 'error': response.json().get("error")}
        else:
            return {'success': False, 'error': f'Unknown error adding word to Anki: {response_json}'}
