#!/bin/bash

SERVER_PORT=$1
# set the database dns name to externameName
export EXTERNAL_NAME=$PSQL_HOSTNAME
export SERVER_PORT=$SERVER_PORT
cat ../services.yml | envsubst | kubectl replace --force -f - ;