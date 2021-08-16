#!/bin/bash

## Required args
export SERVER_PORT=$1                   # web server port nuumber in production
OPENHCS_IMAGE=$2
export ENVIRONMENT=production;          # must be production
export DEPLOYMENT_NAME="$ENVIRONMENT-ohcs-dpy"


# Get deployments on stagging environment to productions
# GET in production Loadbalancer service externalName
ExternalName=$(kubectl get services -n default -l environ=production,tier=backend -o=jsonpath="{.status.loadBalancer.ingress[*].ip}")

# Set the Server DNS Name in the Server's ConfigMap
export SERVER_HOSTNAME=$ExternalName
kubectl get configmap production-svrconfig -n default -o yaml | envsubst | kubectl apply -f - ;

# Replace the namespace and contexts, force replace the in production deployments with new one.
VERSION=$(kubectl get deployments -n default -l environ=stagging,tier=backend,context=green -o jsonpath="{.items[0].metadata.labels.version}");

./xbin/deploy-init.sh $ENVIRONMENT $SERVER_PORT $VERSION $OPENHCS_IMAGE ;


# Retrieve deployments in production namespace and retire all with context==blue
sleep 10s
kubectl get deployments
sleep 10s
kubectl describe deployments/$DEPLOYMENT_NAME --namespace default

VERSION_PRO=$( kubectl  get deployments -n default -l environ=production,tier=backend,version="$VERSION" -o jsonpath="{.items[0].metadata.labels.version}");

#  Compare the version and delete the stagging version
if [[  "$VERSION" == "$VERSION_PRO"  ]]; then 

    # Test in production accessibility
    STATUS=$( curl http://"$SERVER_HOSTNAME":"$SERVER_PORT" )
    if [[ "$STATUS" = *"ok"* ]]; then
        # Delete stagging deployments
        kubectl delete deployments/stagging-ohcs-dpy;
    else
        exit 1;
    fi;

else
    exit 1;

fi;

