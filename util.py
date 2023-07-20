import re
import time


def strip_gender_prefix(spanish_word):
    return re.sub(r'^El ', '', re.sub(r'^La ', '', spanish_word))


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
