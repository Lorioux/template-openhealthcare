#!/bin/bash 

# Install cluster configuaration tools
if [ -e '/usr/local/bin/eksctl' ]; then 
    echo "Found eksctl"; \
else \
    curl --silent --location \
        "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp &&\
    sudo mv /tmp/eksctl /usr/local/bin
fi
sudo export PATH=$PATH:/usr/local/bin &&\
exit 0