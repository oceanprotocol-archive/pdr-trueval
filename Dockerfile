##
## Copyright 2023 Ocean Protocol Foundation
## SPDX-License-Identifier: Apache-2.0
##
FROM python:3.8
LABEL maintainer="Ocean Protocol <devops@oceanprotocol.com>"
RUN apt-get update && apt-get install --no-install-recommends -y strace
COPY . /pdr-trueval
WORKDIR /pdr-trueval
RUN pip install -r requirements.txt
ENV RPC_URL="http://127.0.0.1:8545"
ENV SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
ENV PRIVATE_KEY="0xc594c6e5def4bab63ac29eed19a134c130388f74f019bc74b8f4389df2837a58"
ENV WAIT_FOR_SUBGRAPH=false
ENV PYTHONUNBUFFERED=1
ENV DELAYED_STARTUP=1
ENTRYPOINT ["/pdr-trueval/docker-entrypoint.sh"]
