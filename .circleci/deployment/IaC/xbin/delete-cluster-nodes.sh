#!/bin/bash 


# start deleting if not empty
aws cloudformation delete-stack --stack-name $CLUSTER_STACK_NAME --region "${AWS_DEFAULT_REGION}" ;  
 
echo -e "$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text)\n"
# retrieve cluster core stack status
until [[ -z $(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text | egrep "DELETE_IN_PROGRESS" ) ]]; do
    sleep 15s
    echo "Waiting stack delete complete: DELETE_IN_PROGRESS"
done;

exit 0;