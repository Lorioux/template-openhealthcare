#!/bin/bash

CONFIGS=$1

if [[ -z "$CONFIGS" ]]; then
    echo -e "Please provide the configuration file.\nUsage: configs-init.sh <ConfigMaps.yml>"
    exit 1;
fi;

export HOSTNAME_STAG=$(kubectl get service openhcs-green -o jsonpath="{.status.loadBalancer.ingress[0].ip}" )
if [[ -z "$HOSTNAME_STAG" ]]; then 
    export HOSTNAME_STAG=$(kubectl get service openhcs-green -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" )
    if [[ -z "$HOSTNAME_STAG" ]]; then
        echo "No staging server IP or Hostname"
        exit 1;
    fi;
fi;

export HOSTNAME_PRO=$(kubectl get service openhcs-blue -o jsonpath="{.status.loadBalancer.ingress[0].ip}" )
if [[ -z "$HOSTNAME_PRO" ]]; then 
    export HOSTNAME_PRO=$( kubectl get service openhcs-blue -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" )
    if [[ -z "$HOSTNAME_PRO" ]]; then
        echo "No production server IP or Hostname"
        exit 1;
    fi;
fi;

echo -e "HOSTNAMES: $HOSTNAME_STAG $HOSTNAME_PRO \n"

# Update the server hostname for this environ, IF needed
export SERVER_HOSTNAME_STAG="$HOSTNAME_STAG";
export SERVER_HOSTNAME_PRO="$HOSTNAME_PRO";

cat "$CONFIGS" | envsubst | kubectl replace --force -f - ;

exit 0;
