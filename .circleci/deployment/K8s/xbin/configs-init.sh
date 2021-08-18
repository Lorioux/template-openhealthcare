#!/bin/bash

CONFIGS=$1

if [[ -z "$CONFIGS" ]]; then
    echo -e "Please provide the configuration file.\nUsage: configs-init.sh <ConfigMaps.yml>"
    exit 1;
fi;
STAGG_LB_IP=$(kubectl get services -n default -l environ=staging,tier=backend -o=jsonpath="{.items[0].status.loadBalancer.ingress[*].ip}")

PRO_LB_IP=$(kubectl get services -n default -l environ=production,tier=backend -o=jsonpath="{.items[0].status.loadBalancer.ingress[*].ip}")

# Update the server hostname for this environ, IF needed
export SERVER_HOSTNAME_STAG=$STAGG_LB_IP;
export SERVER_HOSTNAME_PRO=$PRO_LB_IP;

cat $CONFIGS | envsubst | kubectl replace --force -f - ;
echo -e " $PRO_LB_IP $STAGG_LB_IP \n"
exit 0;
