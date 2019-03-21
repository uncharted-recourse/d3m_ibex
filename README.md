## Ibex Named Entity Extraction GRPC Wrapper

This repository provides a GRPC interface to New Knowledge's d3m_ibex named entity extraction primitive.

## Installation

Perform the following command:

```bash
pip3 install git+https://github.com/uncharted-recourse/d3m_ibex 
```

## Example of Running the Code

Make any needed changes to the `config.ini` file, for example, to change the default port.

Start the server:
```python3.6 ibex_server.py```

In a separate terminal session, run the client example:
```python3.6 ibex_client.py```

* Input messages are instances of the `Message` class.
* Extracted named entities are included in the `result` as an instance of the `Extraction` class. See https://github.com/uncharted-recourse/grapevine/blob/master/grapevine/grapevine.proto. 


# gRPC Dockerized Summarization Server

The gRPC interface consists of the following components:
*) `grapevine.proto` in `protos/` which generates `grapevine_pb2.py` and `grapevine_pb2_grpc.py` according to instructions in `protos/README.md` -- these have to be generated every time `grapevine.proto` is changed
*) `ibex_server.py` which is the main gRPC server, serving on port `50053` (configurable via `config.ini`)
*) `ibex_client.py` which is an example script demonstrating how the main gRPC server can be accessed to extract named entities 
 
To build corresponding docker image:
`sudo docker build -t docker.ased.uncharted.software/nk-ibex-named-entity-extraction-binary:latest .`

To run docker image, simply do
`sudo docker run -it -p 50053:50053 docker.ased.uncharted.software/nk-ibex-named-entity-extraction-binary:latest`

Finally, edit `ibex_client.py` with example email of interest for named entity extraction, and then run that script as
`python3 ibex_client.py`

