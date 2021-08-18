#!/bin/bash

SVC_CONFIG=$2 # services configuration file
# set the database dns name to externameName
usage (){
    echo -e "services-init.sh <port-number> <services-config-file>\n"
}

if [[ -z "$1" ]]; then 
    echo -e "Provide service port number\n";
    usage;
    exit 1;
elif [[ -z "$2" ]]; then 
    echo -e "Provide service config file\n";
    usage;
    exit 1;
else 
    export EXTERNAL_NAME=$PSQL_HOSTNAME
    export SERVER_PORT=$1
    cat "$SVC_CONFIG" | envsubst | kubectl apply -f - ;
    sleep 120s
fi;

