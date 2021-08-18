#!/bin/bash

STATUS=$(aws cloudformation list-stacks --query "StackSummaries[?StackName=='$1'].StackStatus| [0]" )
STACKSTATUS=( CREATE_IN_PROGRESS ROLLBACK_IN_PROGRESS DELETE_INPROGRESS )
if [[  "${STACKSTATUS[@]}" != "$STATUS" ]];  then 
    watch -p -n 5 -x echo $STATUS  
    aws cloudformation deploy\
        --stack-name $1 \
        --template-file $2 \
        --region $3 --capabilities "CAPABILITY_IAM" "CAPABILITY_NAMED_IAM"\
        --parameter-overrides ClusterIaCStackName=$4


exit 0

