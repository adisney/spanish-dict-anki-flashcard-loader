import json
from termcolor import colored
from enum import Enum

import util
import anki


class AddNoteOptions(Enum):
    CONTINUE = 0
    ABORT = 1
    CUSTOM = 2


def sync_anki_collection():
    print('Syncing collection')
    anki.sync_anki_collection()

    message = colored(
        'Refer to the Anki desktop app... did syncing complete successfully? (y/N): ',
        'yellow'
    )
    if not util.should_proceed_on_user_input(message):
        raise Exception('Failed to sync collection')


def customize_note_fields(note):
    print()
    print("Current note is:")
    print(json.dumps(note, indent=4, ensure_ascii=False))

    options = [util.UserInputOption(k, (k, v)) for k, v in note["fields"].items()]
    options.insert(0, util.UserInputOption("Done customizing...", False))
    to_customize = util.user_select_option(colored("What field would you like to modify?", "yellow"), options)
    if not to_customize:
        print("Done customizing note.")
        return note
    else:
        key, value = to_customize
        print("Customizing...")
        print("")
        print(f"Current value for {colored(key, 'green')} is {colored(value, 'yellow')}.")
        new_value = input("What should the new value be? : ")
        print("")
        print("Updating value...")
        note["fields"][key] = new_value

    return customize_note_fields(note)


def add_word_to_anki(word):
    print()

    note = anki.build_note(word)
    add_note_to_anki(note)


def add_note_to_anki(note):
    print(colored('Adding the following note to Anki:', 'yellow'))
    print(json.dumps(note, indent=4, ensure_ascii=False))
    print()

    options = [
        util.UserInputOption("No", AddNoteOptions.ABORT),
        util.UserInputOption("Yes", AddNoteOptions.CONTINUE),
        util.UserInputOption("Customize note", AddNoteOptions.CUSTOM),
    ]
    result = util.user_select_option(colored('Do you want to proceed?', 'yellow'), options)
    if result == AddNoteOptions.ABORT:
        print(colored('Not adding word...', 'red'))
    elif result == AddNoteOptions.CONTINUE:
        result = anki.add_note_to_collection(note)

        if 'error' in result:
            print(f'{colored("Error adding word to Anki:", "light_red")} {result["error"]}')
        else:
            print(colored('Word added to Anki flashcards successfully.', 'cyan'))
    elif result == AddNoteOptions.CUSTOM:
        new_note = customize_note_fields(note)
        add_note_to_anki(new_note)


def find_potential_conflicts(word, notes):
    details = anki.find_anki_note_details(notes)

    print()
    print(f"{colored('Potential conflicts for', 'light_red')} {colored(word.spanish, 'green')}{colored(':', 'light_red')}")
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
            print('Not adding word to deck...')
