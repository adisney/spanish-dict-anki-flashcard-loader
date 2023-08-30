from termcolor import colored
import argparse

import util
import spanish_dict
import commands


def add_words_of_the_day(args):
    commands.sync_anki_collection()
    util.filler_progress_bar()

    cache = util.loadDateCache(args.cache_file)

    print('Getting all the currently available words')
    util.filler_progress_bar()

    words = spanish_dict.get_current_words_of_the_day()
    print(f'Received {len(words)} words')
    for word in words:
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

    util.updateCache(cache, args.cache_file)
    print()
    print(colored("All done! Study hard!", "yellow"))


print(colored("Let's add some new words to your flash cards!", "yellow"))
util.filler_progress_bar()

parser = argparse.ArgumentParser(
                    prog='WordOfTheDay',
                    description='Add SpanishDict\'s Words of the Day to Anki')
parser.add_argument('-c', '--cache_file', help='Directory containing the date cache', default='./.data')
args = parser.parse_args()

add_words_of_the_day(args)
