#!/bin/sh

FILENAME=$1

#mkdir /results

if [[ "$FILENAME" == *".hex" ]]; then
    python3.7 analyzeBytecode.py "$FILENAME"
else
    for c in `python3.7 printContractNames.py ${FILENAME}`; 
    do 
        path_contract=$(echo "$1" | sed -e 's/^\///')
        manticore --no-colors --contract ${c} $path_contract
        mv /mcore_* /results
    done
fi