#!/bin/bash

CONFIGS_FILE=$1

STAGG_LB_IP=$(kubectl get services -n default -l environ=staging,tier=backend -o=jsonpath="{.items[0].status.loadBalancer.ingress[*].ip}")

PRO_LB_IP=$(kubectl get services -n default -l environ=production,tier=backend -o=jsonpath="{.items[0].status.loadBalancer.ingress[*].ip}")

# Update the server hostname for this environ, IF needed
export SERVER_HOSTNAME_STAG=$STAGG_LB_IP;
export SERVER_HOSTNAME_PRO=$PRO_LB_IP;

cat $CONFIGS_FILE | envsubst | kubectl replace --force -f - ;
echo $PRO_LB_IP $STAGG_LB_IP
exit 0;
