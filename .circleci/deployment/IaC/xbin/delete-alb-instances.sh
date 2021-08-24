#!/bin/bash

# get cluster nodes DELETION status 
status=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text )

if [[ "$status" == "DELETE_COMPLETE" ]]; then 

    # get all alb dns name from config maps 
    ALB_STAG=$(kubectl get configmap -n deafult -l environ='staging',app='openhcs' -o jsonpath="{.items[0].data.SERVER_HOSTNAME}" )
    ALB_PROD=$(kubectl get configmap -n deafult -l environ='production',app='openhcs' -o jsonpath="{.items[0].data.SERVER_HOSTNAME}")

    # Find and delete 
    for ELB in "$ALB_STAG" "$ALB_PROD" ; do
    echo -e "Deleting ELB: $ELB \n"; 
    echo $(aws elb describe-load-balancers --output text  \
        --query "LoadBalancerDescriptions[?(LoadBalancerDnsName=='$ELB')].LoadBalancerName" \
        --output text ) | aws elb delete-load-balancer --load-balancer-name $1 --profile default;
    done;

fi;