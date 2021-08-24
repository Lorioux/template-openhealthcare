#!/bin/bash

criteria=$1

delete_all_exclude_vpc(){

    # check the status of cluster core stack, 'DELETE_COMPLETE' to proceed
    STATUS=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text );

    until [[ -z $(echo "$STATUS" | egrep "DELETE_COMPLETE" )  ]]; do
        echo -e "CLUSTER STATUS: DELETE_NOT_COMPLETE\n";
        STATUS=$(aws cloudformation describe-stacks --query "Stacks[?(StackName=='${CLUSTER_STACK_NAME}')].StackStatus" --output text );
    done;

    
    if [[ "$STATUS" == "DELETE_COMPLETE" || -z "$STATUS" ]]; then
        echo -e "DELETING STACK: ${CLUSTER_IAC_STACK_NAME}\n"; 
        aws cloudformation delete-stack --stack-name "${CLUSTER_IAC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}" ; 

    fi;

}

delete_include_vpc(){

    # find vpc logical ID
    VPC_ID=$(aws cloudformation list-exports \
            --no-paginate \
            --output text \
            --query "Exports[?(Name=='${CLUSTER_IAC_STACK_NAME}::VPC')].Value" );


    # delete VPC and remaining associated EKS security groups
    if [[ -n "$VPC_ID" ]]; then

        # Get all NI associatiate with the VPC
        NIFs=($(aws ec2 describe-network-interfaces --no-paginate --filter Name=vpc-id,Values="$VPC_ID" --query "NetworkInterfaces[*].NetworkInterfaceId" --output text ) )

        # Get all security groups
        SCGs=($(aws ec2 describe-security-groups --no-paginate --filter Name=vpc-id,Values="$VPC_ID" --query "SecurityGroups[?(GroupName!='default')].GroupId" --output text ) )
        

        ResourceStatus="DELETE_IN_PROGRESS"
        until [[ "$ResourceStatus" == "DELETE_COMPLETE" ]]; do 
            ResourceStatus=$( aws cloudformation describe-stack-resources \
                        --stack-name "${CLUSTER_IAC_STACK_NAME}" \
                        --output text \
                        --query "StackResources[?(ResourceType=='AWS::EKS::Cluster') && (PhysicalResourceId=='${CLUSTER_NAME}')].ResourceStatus" )
                        # Wait dependecies to be deleteted
                        echo -e "Cluster Status: $ResourceStatus\n"
                        sleep 15s
        done;

        
        for ni in "${NIFs[@]}" ; do
            aws ec2 delete-network-interface --network-interface-id $ni;
        done;

        
        # delete EKS security group
        for scg in "${SCGs[@]}" ; do
            $(aws ec2 delete-security-group --group-id "$scg" | egrep "DependencyViolation" );
        done;

        # echo -e "Deleting VPC\n"
        aws ec2 delete-vpc --vpc-id $VPC_ID --region "${AWS_DEFAULT_REGION}" --profile default;


        # clean up the network stack
        aws cloudformation delete-stack --stack-name "${CLUSTER_IAC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}";
    fi;
}

case "$criteria" in 

    "exclude-vpc")
        delete_all_exclude_vpc ;
        exit 0;
        ;;

    "include-vpc")
        delete_include_vpc ;
        exit 0;
        ;;
    *)
        echo -e "Provide the criteria: \n one of <exclude-vpc> or <include-vpc>"
        exit 1;
        ;;
esac;