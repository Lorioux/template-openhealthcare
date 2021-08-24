#!/bin/bash

criteria=$@1

case ("$criteria") 

    "exclude-vpc")
        delete_all_exclude_vpc();
        exit 0;
        ;;

    "include-vpc")
        delete_include_vpc();
        exit 0;
        ;;
    *)
        echo "Provide the criteria."
        exit 1;
        ;;
esac;

delete_all_exclude_vpc(){

    # check the status of cluster core stack, 'DELETE_COMPLETE' to proceed
    STATUS=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text )
    until [[ "$status" != "DELETE_COMPLETE"  ]]; do
        echo -e "CLUSTER STATUS: $STATUS\n";
        STATUS=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text );
    done;

    if [[ "$status" == "DELETE_COMPLETE" ]]; then
        echo -e "DELETING STACK: $name\n"; 
        aws cloudformation delete-stack --stack-name "${CLUSTER_IAC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}" --ratain-resource "VPC" ;  
    fi;

}

delete_include_vpc(){

    # find vpc logical ID
    VPC_ID=$(aws cloudformation list-exports --stack-name "${CLUSTER_IAC_STACK_NAME}" \
        --no-paginate \
        --output text
        --query "Exports[?(Name=='${CLUSTER_IAC_STACK_NAME}::VPC')].Value" );

    # delete VPC and remaining associated EKS security groups
    if [[ -n "$VPC_ID"]]; then
        SCGs=($(aws ec2 describe-security-groups --no-paginate --filter Name=vpc-id,Values="$VPC_ID" --query "SecurityGroups[*].GroupId" --output text ) )
        
        # delete EKS security group
        for scg in "${SCGs[@]}" ; do
        aws ec2 delete-security-group --group-id "$scg";
        done;
        echo -e "Deleting VPC\n"
        aws ec2 delete-vpc --vpc-id $VPC_ID --region "${AWS_DEFAULT_REGION}" --profile default;


        # clean up the network stack
        aws cloudformation delete-stack "${CLUSTER_IAC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}";
    fi;
}