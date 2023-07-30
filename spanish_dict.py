import requests
from datetime import datetime
from collections import namedtuple
from bs4 import BeautifulSoup
from itertools import chain
import re

SPANISH_TO_ENGLISH_URL = 'https://www.wordreference.com/es/en/translation.asp?spen='
ENGLISH_TO_SPANISH_URL = 'https://www.wordreference.com/es/translation.asp?tranword='
WORD_OF_THE_DAY_URL = 'https://www.spanishdict.com/wordoftheday'
WORD_DIV_CLASS = 'IvPSNgXy'
MONTH_CLASS = 'jkQASa0U'
DATE_CLASS = 'Pu6E7CK7'
SPANISH_WORD_CLASS = 'tds4TDh9'
ENGLISH_WORD_CLASS = 'W9SgI1ND'
EXAMPLE_PHRASE_CLASS = 'xiQBRZra'
PHRASE_TRANSLATION_CLASS = 'KkXPxEB8'


Word = namedtuple("Word", ["date", "spanish", "english", "example", "translation"])
Definition = namedtuple("Definition", ["from_word", "synonyms", "to_words", "from_example", "to_example"])
ToWord = namedtuple("ToWord", ["classification", "to_word"])


def get_current_words_of_the_day():
    words = []
    current_year = str(datetime.now().year)

    response = requests.get(WORD_OF_THE_DAY_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    word_divs = soup.find_all('div', {'class': WORD_DIV_CLASS})

    for div in word_divs:
        month = div.find('div', {'class': MONTH_CLASS}).text
        day = div.find('div', {'class': DATE_CLASS}).text
        word_date = f'{current_year}-{month}-{day}'
        spanish_word = div.find('a', {'class': SPANISH_WORD_CLASS}).text.capitalize()
        english_word = div.find('div', {'class': ENGLISH_WORD_CLASS}).text.capitalize()
        example_phrase = div.find('div', {'class': EXAMPLE_PHRASE_CLASS}).text
        phrase_translation = div.find('div', {'class': PHRASE_TRANSLATION_CLASS}).text

        words.append(Word(word_date, spanish_word, english_word, example_phrase, phrase_translation))

    return words


def get_def_es_en(english_word):
    return get_def(f'{SPANISH_TO_ENGLISH_URL}{english_word}')


def get_def_en_es(spanish_word):
    return get_def(f'{ENGLISH_TO_SPANISH_URL}{spanish_word}')


def get_def(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Failure finding definition')

    soup = BeautifulSoup(response.text, 'html.parser')
    defs = soup.find_all('table', {'class': 'WRD'})
    rows = chain.from_iterable([d.find_all('tr') for d in defs])

    current_class = 'even'
    from_word = ''
    from_example = ''
    to_words = []
    to_example = ''
    synonym = ''
    possibleDefinitions = []

    for r in rows:
        if r.has_attr('class') and (r['class'][0] == 'even' or r['class'][0] == 'odd'):
            if from_word and r['class'][0] != current_class:
                to_words = [ToWord(c, t) for c, t in to_words]
                newDefinition = Definition(from_word,
                                           synonym,
                                           to_words,
                                           from_example,
                                           to_example)
                possibleDefinitions.append(newDefinition)

                current_class = 'odd' if current_class == 'even' else 'even'
                from_word = ''
                from_example = ''
                to_words = []
                to_example = ''
                synonym = ''

            tds = r.find_all('td')
            # Gather the word being defined, word definitions, classification and synonyms
            if len(tds) == 3:
                # Get the from_word aka the word being defined
                if tds[0].has_attr('class') and tds[0]['class'][0] == 'FrWrd':
                    from_word = tds[0].find('strong').text
                    from_word = re.sub("⇒", '', from_word)

                # Get the synonyms and/or classification of the word if available
                classification = tds[1].find('span').text if tds[1].find('span') else ''
                if classification and not synonym:
                    synonym = tds[1].text.replace(classification, '')
                    synonym = synonym.strip()

                # Get one of the to_words aka the definitions
                type_of_word = tds[2].find('em').text
                defn = re.sub(f'{type_of_word}$', '', tds[2].text).strip()
                defn = re.sub("⇒", '', defn)
                to_words.append((classification, defn))
            # See if we can get some example sentences
            elif len(tds) == 2:
                example = tds[1].find('span')
                if example and tds[1].has_attr('class') and tds[1]['class'][0] == 'FrEx':
                    from_example = example.text
                elif example and tds[1].has_attr('class') and tds[1]['class'][0] == 'ToEx':
                    to_example = example.text

    return possibleDefinitions
