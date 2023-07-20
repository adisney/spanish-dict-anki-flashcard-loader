from termcolor import colored

import anki
import util
import spanish_dict
import commands


def main():
    commands.sync_anki_collection()
    util.filler_progress_bar()

    cache = util.loadDateCache()

    print('Getting all the currently available words')
    util.filler_progress_bar()

    for word in spanish_dict.get_current_words_of_the_day():
        if word.date in cache:
            print(f'Word from {word.date} already in cache. Moving to next one.')
        else:
            cache.add(word.date)
            print(f'Found candidate: {colored(word.spanish, "green")} - {word.english}')
            commands.try_add_word(word)

        util.filler_progress_bar()

    try:
        commands.sync_anki_collection()
    except Exception:
        print(colored('Failed syncing the collection during cleanup. Must manually sync collection', 'light_red'))

    util.updateCache(cache)
    print()
    print(colored("All done! Study hard!", "yellow"))


print(colored("Let's add some new words to your flash cards!", "yellow"))
util.filler_progress_bar()

main()
