from termcolor import colored
from enum import Enum

import util
import spanish_dict
import commands
import argparse


class OriginLanguage(Enum):
    SPANISH = "ES"
    ENGLISH = "EN"


def get_spanish_translation(args):
    get_translation(spanish_dict.get_def_en_es, args.word, OriginLanguage.ENGLISH, args)


def get_english_translation(args):
    get_translation(spanish_dict.get_def_es_en, args.word, OriginLanguage.SPANISH, args)


def get_translation(def_func, word, originLanguage, args):
    print("")
    print(f"Getting definition for {colored(word, 'green')}")
    definitions = def_func(word, args.count)

    print("")
    print(f"Found {colored(len(definitions), 'yellow')} definitions")
    print("")
    for d in definitions:
        print(f"{colored(d.from_word, 'green')}:")
        if d.synonyms:
            print(f"\t{colored('Synonyms', 'yellow')} - {d.synonyms}")
        print(f"{colored('Translations', 'yellow')}:")
        for t in d.to_words:
            print(f"\t- {t.to_word} {t.classification if t.classification else ''}")

    print("")
    if len(definitions) == 0:
        print(colored("No definitions found. Exiting...", "light_red"))
    else:
        message = colored(f"{colored('Would you like to add one of these definitions to Anki?', 'yellow')} (y/N): ")
        if util.should_proceed_on_user_input(message):
            if not args.no_sync:
                commands.sync_anki_collection()

            options = []
            for d in definitions:
                for t in d.to_words:
                    data = spanish_dict.Word("", d.from_word, t.to_word, d.from_example, d.to_example)
                    if originLanguage == OriginLanguage.ENGLISH:
                        data = spanish_dict.Word("", t.to_word, d.from_word, d.to_example, d.from_example)
                    options.append(util.UserInputOption(f"{d.from_word} ⇒ {t.to_word}", data))
            translation_to_add = util.user_select_option('Select which translation to add...', options)

            commands.try_add_word(translation_to_add)


def main():
    parser = argparse.ArgumentParser(
                        prog='Check Translation',
                        description='Obtains the Spanish or English translation of a word')
    subparsers = parser.add_subparsers(required=True)

    spanish_to_english_parser = subparsers.add_parser('esen')
    spanish_to_english_parser.add_argument('word', help='The word to translate')
    spanish_to_english_parser.add_argument('-n', '--no_sync', help='Do not sync the collection', default=False, action='store_true')
    spanish_to_english_parser.add_argument('-c', '--count', help='Max number of translations to display', type=int, default=5)
    spanish_to_english_parser.set_defaults(func=get_english_translation)

    english_to_spanish_parser = subparsers.add_parser('enes')
    english_to_spanish_parser.add_argument('word', help='The word to translate')
    english_to_spanish_parser.add_argument('-n', '--no-sync', help='Do not sync the collection', default=False, action='store_true')
    english_to_spanish_parser.add_argument('-c', '--count', help='Max number of translations to display', type=int, default=5)
    english_to_spanish_parser.set_defaults(func=get_spanish_translation)

    args = parser.parse_args()
    args.func(args)


print("")

main()
