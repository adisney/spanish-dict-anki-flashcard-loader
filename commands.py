import json
from termcolor import colored

import util
import anki


def sync_anki_collection():
    print('Syncing collection')
    anki.sync_anki_collection()

    message = colored(
        'Refer to the Anki desktop app... did syncing complete successfully? (y/N): ',
        'yellow'
    )
    if not util.should_proceed_on_user_input(message):
        raise Exception('Failed to sync collection')


def add_word_to_anki(word):
    print()

    note = anki.build_note(word)

    print(colored('Adding the following note to Anki:', 'yellow'))
    print(json.dumps(note, indent=4, ensure_ascii=False))
    print()

    if util.should_proceed_on_user_input('Do you want to proceed? (y/N): '):
        result = anki.add_note_to_collection(note)

        if 'error' in result:
            print(f'{colored("Error adding word to Anki:", "light_red")} {result["error"]}')
        else:
            print(colored('Word added to Anki flashcards successfully.', 'cyan'))
    else:
        print('Not adding word...')


def find_potential_conflicts(word, notes):
    details = anki.find_anki_note_details(notes)

    print()
    print(colored(f'Potential conflicts for {word.spanish}:', "light_red"))
    for detail in details:
        print(f'\t{colored("Conflict", "light_red")}:')
        for key, value in detail.get('fields').items():
            print(f'\t\t{key}: {value.get("value")}')


def try_add_word(word):
    notes = anki.find_anki_notes(util.strip_gender_prefix(word.spanish))
    if not anki.word_already_in_deck(notes):
        print('No conflicts found')
        add_word_to_anki(word)
    else:
        find_potential_conflicts(word, notes)

        print()
        if util.should_proceed_on_user_input(f'Do you want to continue adding the word {colored(word.spanish, "green")}? (y/N): '):
            add_word_to_anki(word)
        else:
            print('Skipping...')
