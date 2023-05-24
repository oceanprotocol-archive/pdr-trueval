#!/bin/bash
if [ "${WAIT_FOR_SUBGRAPH}" = "true" ]
then
  echo "Waiting for subgraph to be ready...."
  while [ ! -f "/ocean-subgraph/ready" ]; do
    sleep 2
  done
fi
cd /pdr-trueval/
echo "Starting app..."
/usr/local/bin/python -u main.py

