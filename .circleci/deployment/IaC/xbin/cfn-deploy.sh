#!/bin/bash

aws cloudformation deploy --stack-name $1 --template-file $2 --region $3 --capabilities "CAPABILITY_IAM" "CAPABILITY_NAMED_IAM" --parameter-overrides ClusterIaCStackName=$4


exit 0

