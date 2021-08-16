#!/bin/bash 

# Having deployed the cluster successfully. Need to update the loggins types 
eksctl utils update-logging --cluster $CLUSTERNAME --region $AWS_DEFAULT_REGION &&\

# After logging update successfully, write the kubernetes authentication config
ekscl utils write-kubeconfig --cluster $CLUSTERNAME --region $AWS_DEFAULT_REGION &&\

exit 0

# General flags:
#   -n, --name string               EKS cluster name (generated if unspecified, e.g. "ferocious-party-1628768155")
#       --tags stringToString       Used to tag the AWS resources. List of comma separated KV pairs "k1=v1,k2=v2" (default [])        
#   -r, --region string             AWS region
#       --with-oidc                 Enable the IAM OIDC provider
#       --zones strings             (auto-select if unspecified)
#       --version string            Kubernetes version (valid options: 1.16, 1.17, 1.18, 1.19, 1.20, 1.21) (default "1.20")
#   -f, --config-file string        load configuration from a file (or stdin if set to '-')
#       --timeout duration          maximum waiting time for any long-running operation (default 25m0s)
#       --install-vpc-controllers   Install VPC controller that is required for Windows workloads
#       --fargate                    Create a Fargate profile scheduling pods in the default and kube-system namespaces onto Fargate   
#       --dry-run                   Dry-run mode that skips cluster creation and outputs a ClusterConfig

# Initial nodegroup flags:
#       --nodegroup-name string          name of the nodegroup (generated if unspecified, e.g. "ng-47bdc104")
#       --without-nodegroup              if set, initial nodegroup will not be created
#   -t, --node-type string               node instance type
#   -N, --nodes int                      total number of nodes (for a static ASG) (default 2)
#   -m, --nodes-min int                  minimum nodes in ASG (default 2)
#   -M, --nodes-max int                  maximum nodes in ASG (default 2)
#       --node-volume-size int           node volume size in GB (default 80)
#       --node-volume-type string        node volume type (valid options: gp2, gp3, io1, sc1, st1) (default "gp3")
#       --max-pods-per-node int          maximum number of pods per node (set automatically if unspecified)
#       --ssh-access                     control SSH access for nodes. Uses ~/.ssh/id_rsa.pub as default key path if enabled
#       --ssh-public-key string          SSH public key to use for nodes (import from local path, or use existing EC2 key pair)       
#       --enable-ssm                     Enable AWS Systems Manager (SSM)
#       --node-ami string                'auto-ssm', 'auto' or an AMI ID (advanced use)
#       --node-ami-family string         'AmazonLinux2' for the Amazon EKS optimized AMI, or use 'Ubuntu2004' or 'Ubuntu1804' for the 
#                                          official Canonical EKS AMIs (default "AmazonLinux2")
#   -P, --node-private-networking        whether to make nodegroup networking private
#       --node-security-groups strings   attach additional security groups to nodes
#       --node-labels stringToString     extra labels to add when registering the nodes in the nodegroup. List of comma separated KV pairs "k1=v1,k2=v2" (default [])
#       --node-zones strings             (inherited from the cluster if unspecified)
#       --instance-prefix string         add a prefix value in front of the instance's name
#       --instance-name string           overrides the default instance's name
#       --disable-pod-imds               Blocks IMDS requests from non-host networking pods
#       --managed                        Create EKS-managed nodegroup (default true)
#       --spot                           Create a spot nodegroup (managed nodegroups only)
#       --instance-types strings         Comma-separated list of instance types (e.g., --instance-types=c3.large,c4.large,c5.large    

# Cluster and nodegroup add-ons flags:
#       --asg-access               enable IAM policy for cluster-autoscaler
#       --external-dns-access      enable IAM policy for external-dns
#       --full-ecr-access          enable full access to ECR
#       --appmesh-access           enable full access to AppMesh
#       --appmesh-preview-access   enable full access to AppMesh Preview
#       --alb-ingress-access       enable full access for alb-ingress-controller
#       --install-neuron-plugin    install Neuron plugin for Inferentia nodes (default true)
#       --install-nvidia-plugin    install Nvidia plugin for GPU nodes (default true)

# VPC networking flags:
#       --vpc-cidr ipNet                 global CIDR to use for VPC (default 192.168.0.0/16)
#       --vpc-private-subnets strings    re-use private subnets of an existing VPC
#       --vpc-public-subnets strings     re-use public subnets of an existing VPC
#       --vpc-from-kops-cluster string   re-use VPC from a given kops cluster
#       --vpc-nat-mode string            VPC NAT mode, valid options: HighlyAvailable, Single, Disable (default "Single")

# Instance Selector options flags:
#       --instance-selector-vcpus int                 an integer value (2, 4 etc)
#       --instance-selector-memory string             4 or 4GiB
#       --instance-selector-cpu-architecture string   x86_64, or arm64
#       --instance-selector-gpus int                  an integer value

# AWS client flags:
#   -p, --profile string         AWS credentials profile to use (overrides the AWS_PROFILE environment variable)
#       --cfn-role-arn string    IAM role used by CloudFormation to call AWS API on your behalf
#       --cfn-disable-rollback   for debugging: If a stack fails, do not roll it back. Be careful, this may lead to unintentional resource consumption!

# Output kubeconfig flags:
#       --kubeconfig string               path to write kubeconfig (incompatible with --auto-kubeconfig) (default "C:\\Users\\magid\\.kube\\config")
#       --authenticator-role-arn string   AWS IAM role to assume for authenticator
#       --set-kubeconfig-context          if true then current-context will be set in kubeconfig; if a context is already set then it will be overwritten (default true)
#       --auto-kubeconfig                 save kubeconfig file by cluster name, e.g. "C:\\Users\\magid\\.kube/eksctl/clusters/ferocious-party-1628768155"
#       --write-kubeconfig                toggle writing of kubeconfig (default true)