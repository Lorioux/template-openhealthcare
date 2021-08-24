#!/bin/bash 


# start deleting if not empty
aws cloudformation delete-stack --stack-name $CLUSTER_STACK_NAME --region "${AWS_DEFAULT_REGION}" ;   

# retrieve cluster core stack status
status=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text )
until [[ "$status" == "DELETE_IN_PROGRESS" ]]; do
    sleep 5s
    status=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text )
    Waiting stack delete complete
done;

exit 0;