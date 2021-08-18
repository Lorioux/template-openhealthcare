#!/bin/bash


# Usage template
template="\nUsage: deploy-init.sh <ENVIRONMEN> <SERVER_PORT> <VESION> <DOCKER_IMAGE_PATH> <FILE.yml> \n"


## Required args
export ENVIRONMENT=$1 ;     # environ for the deployment
export SERVER_PORT=$2;      # web server port number
export VERSION=$3;          # deployment version
export OPENHCS_IMAGE=$4 ;   # docker image
FILE=$5
export DEPLOYMENT_NAME="$ENVIRONMENT-ohcs-dpy"; 

usage (){
    
    if  [[ -z "$@1" ]]; then 
        echo "Missing Environment";
        echo $2
        echo -e $template
        exit 1
    elif [[ -z "$@2" ]]; then 
        echo "Missing server port number";
        echo -e $template
        exit 1
    elif [[ -z "$@3"  ]]; then 
        echo "Missing deployment version";
        echo -e $template
        exit 1
    elif [[ -z "$@4" ]]; then 
        echo "Missing docker image path";
        echo -e $template
        exit 1
    elif [[ -z "$@5" ]]; then 
        echo "Missing deployment file";
        echo -e $template
        exit 1
        echo creating deployment ...
        
    else
        echo "All set to run deployment."
    fi;
};

usage;

LOADBL_IP="";       # Load balancer IP 
# Retrieve the loadbalancer domain name for each environment
if [[ -n "$ENVIRONMENT" && "$ENVIRONMENT" == "staging" ]]; then 
    # if [[ -n $(echo "127.0.0.1" | grep -E "^[0-9]{1,3}(\.[0-9]{1,3}){3}$") ]]; then echo TRUE; else echo FALSE; fi; 
    LOADBL_IP=$(kubectl get services -n default -l environ="$ENVIRONMENT",app="openhcs" -o jsonpath="{.items[0].status.loadBalancer.ingress[*].hostname}" )
    # echo "1" $LOADBL_IP
elif [[ -n "$ENVIRONMENT" && "$ENVIRONMENT" == "production" ]]; then
    LOADBL_IP=$(kubectl get services -n default -l environ="$ENVIRONMENT",app="openhcs" -o=jsonpath="{.items[0].status.loadBalancer.ingress[0].hostname}" )
else
    exit 1;
fi;

# Set the external domain name or IP into Server Config Map
if [[ -n "$LOADBL_IP" ]]; then 
    
    # Deploy the application depending on the environment
    if [[ -n "$ENVIRONMENT" ]]; then

        case "$ENVIRONMENT" in 
            # deploy for staging environment as blue context
            staging)
                export CONTEXT=green
                cat "$FILE" | envsubst | kubectl apply --force -f - ;
                ;;
            production)
                # deploy for production environment as blue context
                export CONTEXT=blue
                cat "$FILE" | envsubst | kubectl apply --force -f - ;
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

    





