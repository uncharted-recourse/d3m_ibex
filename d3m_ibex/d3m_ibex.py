''' Extract named entities from documents '''
import os
from typing import List
import re
import string
import spacy

REGEX_FILTERS = {
    re.compile('RT @\w+'): '',  # retweet (filter before removing mentions)
    re.compile('https?://\S+'): '',  # uri
    re.compile('#\w*'): '',  # hashtag
    re.compile('@\w*'): '',  # mention
    # re.compile('\d+'): '',  # number
    # re.compile('[{chars}]'.format(chars=string.punctuation + '¿¡')): '',
    re.compile('\s'): ' ',  # whitespace [ \t\n\r\f\v]
}


SPACES_REGEX = re.compile('  +')


def prep_text(text: str):
    ''' preprocess text, removing content irrelevant for entity recognition or topic selection'''
    for regex, replacement in REGEX_FILTERS.items():
        text = regex.sub(replacement, text)

    # replace multiple whitespaces last to catch those created by substitions above
    return SPACES_REGEX.sub(' ', text)

PARSERS = {}

current_path = os.path.dirname(os.path.abspath(__file__))
exclude_path = os.path.join(current_path, 'exclude_words.txt')
if os.path.isfile(exclude_path):
    with open(exclude_path) as exclude_file:
        EXCLUDE_WORDS = set(word.strip('\n') for word in exclude_file.readlines())
else:
    # TODO move to logger
    print('warning: cannot find exclude_words.txt')
    EXCLUDE_WORDS = set()

LANGUAGES = ['english', 'spanish']  # 'hungarian', 'french', 'italian'

# mapping from language name to name of spacy parser
LANG_TO_PARSER = {
    'english': 'en_core_web_md',
    'spanish': 'es_core_news_md'
}



class Ibex():

    def __init__(self, parser_installation_file = None):
        if parser_installation_file:
            try:
                print("Installing file: %s" % parser_installation_file)
                os.system("pip3 install {0}".format(parser_installation_file))
            except Exception as e:
                print("Problem installing file: %s" % parser_installation_file)
        pass

    def filter_entity(self, entity):
        ''' filter entities identified by spacy. For single-word entities, remove
        those in the exclude list or not proper nouns. for multi-word entities, make
        sure all words are not stop words with some exceptions.
        '''

        if len(entity) == 1:
            # for single word entities, remove if stop word or number
            ent = entity[0]
            return (ent.is_stop or ent.text.lower() in EXCLUDE_WORDS
                    or ent.pos_ != 'PROPN'
                    # or ent.pos_ == 'NUM'
                    # or ent.pos_ == 'PUNCT')
                    )
            # TODO allow single entities that are not tagged as a proper noun?

        # for multi-word entities, remove if there are any stop words with exceptions for some POS
        remove = [(word.is_stop or (word.text.lower() in EXCLUDE_WORDS))
                # allow determiners that are not wh-determiners or interrogatives
                and not (word.pos_ == 'DET' and word.tag_ != 'WDT' and word.tag_ != 'DET__PronType=Int')
                and word.pos_ != 'ADP'  # and adpositions
                for word in entity]

        return any(remove)


    def get_entities(self, document: str, language: str='english'):
        ''' Takes a document and returns a list of extracted entities '''

        if isinstance(document, List):
            document = " ".join(document)
        # if language given is not the name of a spacy parser, try to convert it to one
        parser_name = language if language in LANG_TO_PARSER.values() else LANG_TO_PARSER.get(language.lower())
        if not parser_name:
            raise Exception('language not supported')

        # if requested parser is not already in memory, try to load from spacy
        if parser_name not in PARSERS:
            try:
                PARSERS[parser_name] = spacy.load(parser_name)
            except Exception as e:
                # Try downloading the needed spacy parser
                # install spacy parsers
                os.system("python3 -m spacy download {0}".format(LANG_TO_PARSER[language]))
                PARSERS[parser_name] = spacy.load(parser_name)

        def get_ents(doc):
            ''' prep, parse, then extract entities from doc text '''
            doc = prep_text(doc)  # preprocess string
            doc = PARSERS[parser_name](doc)  # parse prepped doc
            ents = set(ent.text for ent in doc.ents if not self.filter_entity(ent))  # extract entities
            return list(ents)

        return get_ents(document)


if __name__ == '__main__':
    text = 'The Trump administration struggled on Monday to defend its policy of separating parents from their sons and daughters at the southern US border amid growing national outrage and the release of of sobbing children.'
    #client = Ibex()
    client = Ibex(parser_installation_file = '/tmp/f54a6e6a2ff34c1adb1a2eabeb67b170933453ed878125c76813dc2e31c8cf8a/en_core_web_md-2.1.0a7.tar.gz')
    result = client.get_entities(text)
    print(result)
