#!/bin/bash 

FILE=$1
# NAMESPACE=$2

# check if secret_key is set.
CHECKSECRET=$SECRET_KEY

if [[ -z '$PSQL_HOSTNAME' ]]; then
    exit 1;

elif [[ -z '$PSQL_PASSWORD' ]]; then
    exit 1;

elif [[ -z '$PSQL_USERNAME' ]]; then
    exit 1;

else
    if [[ -z "$CHECKSECRET" ]]; then 
        
        SECRET_KEY=$(python -c "import os; print(os.urandom(64).hex('-'))" )
        export SECRET_KEY=$SECRET_KEY;
        # echo -e "\nSECRET_KEY=$SECRET_KEY" >> $FILE
    fi
fi;

cat "$FILE" | envsubst | kubectl apply -f - ;

exit 0;