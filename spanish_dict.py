import requests
from datetime import datetime
from collections import namedtuple
from bs4 import BeautifulSoup
from itertools import chain
import re
from enum import Enum

SPANISH_TO_ENGLISH_URL = 'https://www.wordreference.com/es/en/translation.asp?spen='
ENGLISH_TO_SPANISH_URL = 'https://www.wordreference.com/es/translation.asp?tranword='
WORD_OF_THE_DAY_URL = 'https://www.spanishdict.com/wordoftheday'
WORD_DIV_CLASS = 'eu9Qav45'
MONTH_CLASS = 'uritWpC8'
DATE_CLASS = 'YjvKQUha'
SPANISH_WORD_CLASS = 'MhZ0VHvJ'
ENGLISH_WORD_CLASS = 'UEv2G6u_'
EXAMPLE_PHRASE_CLASS = 'S59euzHw'
PHRASE_TRANSLATION_CLASS = 'al0K82xM'


Word = namedtuple("Word", ["date", "spanish", "english", "example", "translation"])
Definition = namedtuple("Definition", ["from_word", "synonyms", "to_words", "from_example", "to_example"])
ToWord = namedtuple("ToWord", ["classification", "to_word"])


class WordGenderPrefix(Enum):
    UNDEFINED = ""
    MASCULINE = "El"
    FEMININE = "La"

    @staticmethod
    def from_abbrev(noun_abbrev):
        if noun_abbrev == "nf":
            return WordGenderPrefix.FEMININE
        elif noun_abbrev == "nm":
            return WordGenderPrefix.MASCULINE
        else:
            return WordGenderPrefix.UNDEFINED

    @staticmethod
    def from_markup(element):
        word_annotation = element.find('em', class_="POS2")

        if word_annotation:
            return WordGenderPrefix.from_abbrev(word_annotation.text)

        return WordGenderPrefix.UNDEFINED

    def apply_prefix(this, word):
        if this == WordGenderPrefix.UNDEFINED:
            return word

        return f"{this.value} {word}"


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


def get_def_es_en(english_word, count=5):
    return get_def(f'{SPANISH_TO_ENGLISH_URL}{english_word}', count)


def get_def_en_es(spanish_word, count=5):
    return get_def(f'{ENGLISH_TO_SPANISH_URL}{spanish_word}', count)


def get_def(url, num_translations_threshold=5):
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
    from_gender = WordGenderPrefix.UNDEFINED

    def can_finalize_definition(from_word, current_class, row):
        return from_word and row['class'][0] != current_class

    for r in rows:
        if r.has_attr('class') and (r['class'][0] == 'even' or r['class'][0] == 'odd'):
            if can_finalize_definition(from_word, current_class, r):
                to_words = [ToWord(c, t) for c, t in to_words]
                formatted_from_word = from_gender.apply_prefix(from_word).capitalize()
                newDefinition = Definition(formatted_from_word,
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

            if len(possibleDefinitions) >= num_translations_threshold:
                break

            tds = r.find_all('td')
            # Gather the word being defined, word definitions, classification and synonyms
            if len(tds) == 3:
                # Get the from_word aka the word being defined
                if tds[0].has_attr('class') and tds[0]['class'][0] == 'FrWrd':
                    from_word = tds[0].find('strong').text
                    from_word = re.sub("⇒", '', from_word)
                    from_gender = WordGenderPrefix.from_markup(tds[0])

                # Get the synonyms and/or classification of the word if available
                classification = tds[1].find('span').text if tds[1].find('span') else ''
                if classification and not synonym:
                    synonym = tds[1].text.replace(classification, '')
                    synonym = synonym.strip()

                # Get one of the to_words aka the definitions
                type_of_word = tds[2].find('em').text
                to_gender = WordGenderPrefix.from_markup(tds[2])
                defn = re.sub(f'{type_of_word}$', '', tds[2].text).strip()
                defn = re.sub("⇒", '', defn)
                defn = to_gender.apply_prefix(defn).capitalize()
                to_words.append((classification, defn))
            # See if we can get some example sentences
            elif len(tds) == 2:
                example = tds[1].find('span')
                if example and tds[1].has_attr('class') and tds[1]['class'][0] == 'FrEx':
                    from_example = example.text
                elif example and tds[1].has_attr('class') and tds[1]['class'][0] == 'ToEx':
                    to_example = example.text

    return possibleDefinitions
