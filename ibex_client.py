#
# Test GRPC client code for NK Possum text summarization primitive
#
#

from __future__ import print_function
import logging

import grpc
import configparser
import grapevine_pb2
import grapevine_pb2_grpc

logger = logging.getLogger('nk_ibex_client')
logger.setLevel(logging.DEBUG)

DEBUG = True # boolean to specify whether to print DEBUG information

def run():

    channel = grpc.insecure_channel('localhost:' + GRPC_PORT)
    stub = grapevine_pb2_grpc.ExtractorStub(channel)

    testMessage = grapevine_pb2.Message(
        raw="3", # This field is interpreted as the number of summary sentences to return.
        language="en",
        text="The Trump administration struggled on Monday to defend its policy of \
             separating parents from their sons and daughters at the southern US border \
                 amid growing national outrage and the release of of sobbing children.")

    try:
        print(testMessage)
        extraction = stub.Extract(testMessage)
        extracted_entities = extraction.values
        if (DEBUG):
            logger.info("Extracted_entities: ")
            logger.info(extracted_entities)
    except Exception:
        logger.exception("Problem running client to extract entities.")
        raise Exception
    

if __name__ == '__main__':
    logging.basicConfig() 
    config = configparser.ConfigParser()
    config.read('config.ini')
    port_config = config['DEFAULT']['port_config']
    logger.info("using port " + port_config + " ...")
    global GRPC_PORT
    GRPC_PORT = port_config
    run()