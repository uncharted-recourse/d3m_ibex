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

    testMessage1 = grapevine_pb2.Message(
        raw="English test", 
        language="en",
        text="The Trump administration struggled on Monday to defend its policy of \
             separating parents from their sons and daughters at the southern US border \
                 amid growing national outrage and the release of of sobbing children.")

    try:
        logger.info(testMessage1)
        extraction1 = stub.Extract(testMessage1)
        extracted_entities1 = extraction1.values
        if (DEBUG):
            logger.info("Extracted_entities: ")
            logger.info(extracted_entities1)
    except Exception:
        logger.exception("Problem running client to extract entities from message 1.")
        raise Exception

    testMessage2 = grapevine_pb2.Message(
        raw="Spanish test", 
        language="es",
        text="El Comité de Ética, Control y Disciplina de la UEFA multó este jueves con 20.000 euros\
             a Cristiano Ronaldo, delantero de la Juventus, por conducta inapropiada por su gesto tras la victoria de su equipo sobre el Atlético de Madrid en el partido de vuelta de los octavos de final de la Liga de Campeones..")

    try:
        logger.info(testMessage2)
        extraction2 = stub.Extract(testMessage2)
        extracted_entities2 = extraction2.values
        if (DEBUG):
            logger.info("Extracted_entities: ")
            logger.info(extracted_entities2)
    except Exception:
        logger.exception("Problem running client to extract entities from message 2.")
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