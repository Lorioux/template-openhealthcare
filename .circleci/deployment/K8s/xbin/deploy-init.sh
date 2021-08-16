#!/bin/bash

## Required args
ENVIRON=$1;         # environ for the deployment
SERVER_PORT=$2;     # web server port number
VERSION=$3;         # deployment version
OPENHCS_IMAGE=$4;   # docker image
       


LOADBL_IP="";       # Load balancer IP 

# Retrieve the loadbalancer domain name for each environment
if [[ -n "$ENVIRON" && "$ENVIRON" == "stagging" ]]; then 
    # if [[ -n $(echo "127.0.0.1" | grep -E "^[0-9]{1,3}(\.[0-9]{1,3}){3}$") ]]; then echo TRUE; else echo FALSE; fi; 
    LOADBL_IP=$(kubectl get services -n default -l environ="$ENVIRON",app="openhcs" -o=jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}" )
elif [[ -n "$ENVIRON" && "$ENVIRON" == "production" ]]; then
    LOADBL_IP=$(kubectl get services -n default -l environ="$ENVIRON",app="openhcs" -o=jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}" )
else
    exit 1;
fi;


# Set the external domain name or IP into Server Config Map
if [[ -n "$LOADBL_IP" ||  -n $(echo "$LOADBL_IP" | grep -E "^[0-9]{1,3}(\.[0-9]{1,3}){3}$") ]]; then 
    
    # Update the server hostname for this environ, IF needed
    # if [[ "$ENVIRON" == "stagging" ]]; then
    #     export SERVER_HOSTNAME_STAG=$LOADBL_IP;
    # else
    #     export SERVER_HOSTNAME_PRO=$LOADBL_IP;
    # fi;
    # kubectl get configmaps -n default -l environ="$ENVIRON" -o yaml | envsubst | kubectl replace --force -f - ;
    
    # Save the url for testing
    echo "APP_TEST_URL="http://$LOADBL_IP"" > .app_test_url;

    # Deploy the application depending on the environment
    if [[ -n "$ENVIRON" ]]; then
        export ENVIRONMENT=$ENVIRON ;
        export OPENHCS_IMAGE=$OPENHCS_IMAGE ;
        export DEPLOYMENT_NAME="$ENVIRON-ohcs-dpy";
        export VERSION=$VERSION;
        export SERVER_PORT=$SERVER_PORT;

        case "$ENVIRON" in 
            # deploy for stagging environment as blue context
            stagging)
                export CONTEXT=green
                cat ./deployments.yml | envsubst | kubectl apply -f - ;
                ;;
            production)
                # deploy for production environment as blue context
                echo creating
                export CONTEXT=blue
                cat ./deployments.yml | envsubst | kubectl replace --force -f - ;
                ;;
            *)
            exit 1;
            ;;
        esac;

    else
        exit 1;

    fi;
else 
    exit 1;
fi; 


