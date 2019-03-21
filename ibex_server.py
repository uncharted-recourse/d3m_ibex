#!/usr/bin/env python
#
# GRPC Server for NK d3m_ibex named entity extraction primitive
# 
# Uses GRPC service config in protos/grapevine.proto
# 

import nltk.data
import nltk
from random import shuffle
from json import JSONEncoder
from flask import Flask, request

import time
import pandas
import pickle
import numpy as np
import configparser
import os.path
import os
import pandas as pd
import datetime

import grpc
import logging
import grapevine_pb2
import grapevine_pb2_grpc
from concurrent import futures

import logging
from collections import Counter
from d3m_ibex import Ibex

logger = logging.getLogger('nk_ibex_server')
logger.setLevel(logging.DEBUG)

# GLOBALS
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
# LANGUAGE_ABBREVIATIONS = ['da','nl','en','fi','fr','de','hu','it','no','pt','ro','ru','es','sv']
# LANGUAGES = ['danish','dutch','english','finnish','french','german','hungarian','italian','norwegian','portuguese','romanian','russian','spanish','swedish']
LANGUAGE_ABBREVIATIONS = ['en','es']
LANGUAGES = ['english','spanish']
LANGUAGE_MAPPING = dict(zip(LANGUAGE_ABBREVIATIONS, LANGUAGES))

DEBUG = True # boolean to specify whether to print DEBUG information

#-----
class NKIbexEntityExtractor(grapevine_pb2_grpc.ExtractorServicer):

    def __init__(self):
        pass

    # Main extraction function
    def Extract(self, request, context):

        # init Extraction result object
        result = grapevine_pb2.Extraction(
            key = "extracted_entities",
            confidence=0.0,
            model="NK_ibex_entity_extractor",
            version="0.0.1",
        )

        # Get text from input message.
        input_doc = request.text
        logger.debug("Input doc: " + input_doc)

        # Exception cases.
        if (len(input_doc.strip()) == 0) or (input_doc is None):
            return result

        # Check the language of the English. Use English 'en' as the default and fallback option.
        language_abbrev = request.language
        if language_abbrev not in LANGUAGE_ABBREVIATIONS:
            logger.warning("Unknown or unsupported language abbreviation. Using en = English.")
            language_abbrev = "en"

        if language_abbrev in LANGUAGE_MAPPING:
            language = LANGUAGE_MAPPING[language_abbrev]
        else:
            language = "english"

        start_time = time.time()

        TopicExtractor = Ibex(language = language)
        
        try:
            entities = TopicExtractor.get_entities(input_doc)
        except Exception:
            logger.exception("Problem extracting named entities.")
            raise Exception

        elapsed_time = time.time()-start_time
        if (DEBUG):
            logger.info("Total time for entity extraction is : %.2f sec" % elapsed_time)
        
        # Include the summary sentences in the result object.
        try:
            result.values[:] = entities 
        except Exception:
            logger.exception("Problem embedding extracted entities in result object.")
            raise Exception

        return result


#-----
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grapevine_pb2_grpc.add_ExtractorServicer_to_server(NKIbexEntityExtractor(), server)
    server.add_insecure_port('[::]:' + GRPC_PORT)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    port_config = config['DEFAULT']['port_config']
    logger.info("using port " + port_config + " ...")
    global GRPC_PORT
    GRPC_PORT = port_config
    
    serve()