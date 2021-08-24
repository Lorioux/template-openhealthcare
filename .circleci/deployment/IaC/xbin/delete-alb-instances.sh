#!/bin/bash

# get cluster nodes DELETION status 
STATUS=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text )

if [[ "$STATUS" == "CREATE_COMPLETE" || -z $STATUS ]]; then 

    # get all alb dns name from config maps 
    ALB_STAG=$(kubectl get configmap -n default -l environ='staging',app='openhcs' -o jsonpath="{.items[0].data.SERVER_HOSTNAME}" )
    ALB_PROD=$(kubectl get configmap -n default -l environ='production',app='openhcs' -o jsonpath="{.items[0].data.SERVER_HOSTNAME}")

    # Find and delete 
    for ELB in "$ALB_STAG" "$ALB_PROD" ; do
        echo -e "Deleting ELB: $ELB \n"; 
        NAME=$(aws elb describe-load-balancers --output text  \
            --query "LoadBalancerDescriptions[?(DNSName=='$ELB')].LoadBalancerName" );
        aws elb delete-load-balancer --load-balancer-name $NAME;
    done;

fi;