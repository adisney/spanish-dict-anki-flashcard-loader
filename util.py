import re
import readline  # noqa: F401
import time
from collections import namedtuple
from termcolor import colored

UserInputOption = namedtuple('UserInputOption', ('message', 'data'))


def strip_gender_prefix(spanish_word):
    return re.sub(r'^El ', '', re.sub(r'^La ', '', spanish_word))


def should_proceed_on_user_input(message):
    user_input = input(message)
    return user_input.lower() == "y" or user_input.lower() == "Y"


def user_select_option(title, options):
    message = title
    for i, option in enumerate(options):
        message = f'{message}\n\t{str(i+1)}. {option.message}'
    user_input = input(f"{message}\n{colored('Please enter your selection: ', 'yellow')}")
    index = int(user_input) - 1
    if (index > len(options) or index < 0):
        raise Exception('Invalid option chosen')
    return options[index].data


def loadDateCache(cache_dir='./.data/'):
    cache = set()
    try:
        with open(f'{cache_dir}/date_cache.txt', 'r') as dateCacheFile:
            for line in dateCacheFile.readlines():
                cache.add(line.strip())
    except FileNotFoundError:
        pass

    return cache


def updateCache(cache, cache_dir="./.data/"):
    with open(f'{cache_dir}/date_cache.txt', 'w') as dateCacheFile:
        for date in sorted(cache):
            dateCacheFile.write(f'{date}\n')


def filler_progress_bar():
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
    time.sleep(1)
    print(".")
