from termcolor import colored

import anki
import util
import spanish_dict


def main():
    anki.sync_anki_collection()
    util.filler_progress_bar()

    cache = util.loadDateCache()

    print('Getting all the currently available words')
    util.filler_progress_bar()

    for word in spanish_dict.get_current_words():
        if word.date in cache:
            print(f'Word from {word.date} already in cache. Moving to next one.')
        else:
            cache.add(word.date)

            print(f'Found candidate: {colored(word.spanish, "green")} - {word.english}')

            notes = anki.find_anki_notes(word.spanish)
            if not anki.word_already_in_deck(notes):
                print('No conflicts found')
                anki.add_word_to_anki(word)
            else:

                if notes:
                    details = anki.find_anki_note_details(notes)

                    print()
                    print(colored(f'Potential conflicts for {word.spanish}:', "light_red"))
                    for detail in details:
                        print(f'\t{colored("Conflict", "light_red")}:')
                        for key, value in detail.get('fields').items():
                            print(f'\t\t{key}: {value.get("value")}')

                print()
                if util.should_proceed_on_user_input(f'Do you want to continue adding the word {colored(word.spanish, "green")}? (y/N): '):
                    anki.add_word_to_anki(word)
                else:
                    print('Skipping...')

        util.filler_progress_bar()

    try:
        anki.sync_anki_collection()
    except Exception:
        print(colored('Failed syncing the collection during cleanup. Must manually sync collection', 'light_red'))

    util.updateCache(cache)
    print()
    print(colored("All done! Study hard!", "yellow"))


print(colored("Let's add some new words to your flash cards!", "yellow"))
util.filler_progress_bar()

main()
