''' Extract named entities from documents '''
import os, sys
from typing import List
import re
import string
import logging
import traceback
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

logger = logging.getLogger('ibex_d3m_wrapper')
logger.setLevel(logging.DEBUG)

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

def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    if len(tb_lines) >1  and len(tb_lines[0])>1:
        logger.log(tb_lines)

class Ibex():


    def __init__(self, parser_installation_file = None, language = None):
        if parser_installation_file:
            self.parser_installation_file = parser_installation_file
            # try:
            #     # print("Uninstalling thinc and cymem")
            #     # os.system("pip3 uninstall --no-input thinc")
            #     # os.system("pip3 uninstall --no-input cymem")
            #     # print("Installing spacy.")
            #     # os.system("pip3 install spacy")
            #     print("Installing file: %s" % self.parser_installation_file)
            #     os.system("pip3 install {0}".format(self.parser_installation_file))

            # except Exception as e:
            #     print("Problem installing file: %s" % self.parser_installation_file)
            #     pass
                


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
        if language == 'spanish':
            try:
                import es_core_news_md
                print("Success importing en_core_web_md")
            except ImportError:
                print("Error importing es_core_news_md")
                sys.exit(-1)
        else:
            try:
                import en_core_web_md
                print("Success importing en_core_web_md")
            except ImportError:
                print("Error importing en_core_web_md")
                sys.exit(-1)

        if isinstance(document, List):
            document = " ".join(document)
        # if language given is not the name of a spacy parser, try to convert it to one
        parser_name = language if language in LANG_TO_PARSER.values() else LANG_TO_PARSER.get(language.lower())
        if not parser_name:
            raise Exception('language not supported')

        # if requested parser is not already in memory, try to load from spacy
        if parser_name not in PARSERS:
            try:
                print("Trying to load parser.")
                if language == 'spanish':
                    PARSERS[parser_name] = es_core_news_md.load()
                else:
                    PARSERS[parser_name] = en_core_web_md.load()
                #PARSERS[parser_name] = spacy.load(parser_name)
            except Exception:
                logger.exception("Problem loading parser")
                print("SECOND ROUND: Try loading again.")
                # os.system("pip3 install spacy")
                # print("Installing file: %s" % self.parser_installation_file)
                # os.system("pip3 install {0}".format(self.parser_installation_file))
                try:
                    if language == 'spanish':
                        PARSERS[parser_name] = es_core_news_md.load()
                    else:
                        PARSERS[parser_name] = en_core_web_md.load()
                except Exception:
                    logger.exception("SECOND ROUND: Problem loading parser")
                    sys.exit(-1)
        else:
            print("Found parser %s in memory" % parser_name)

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
    if len(sys.argv)>=2:
        parser_installation_file = sys.argv[1]
        language = sys.argv[2]
    else:
        parser_installation_file = "en_core_web_md-1.2.1.tar.gz"
        language = "english"
    client = Ibex(parser_installation_file = parser_installation_file, language = language)
    result = client.get_entities(text)
    print(result)
