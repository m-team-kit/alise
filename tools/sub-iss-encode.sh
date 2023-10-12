#!/bin/bash

SUB=$1
ISS=$2

# echo $SUB
# echo $ISS

ENCODED_SUB=`echo -n $SUB | urlencode.py`
ENCODED_ISS=`echo -n $ISS | urlencode.py`

# echo $ENCODED_SUB
# echo $ENCODED_ISS

ENCODED_BOTH=`echo -n ${ENCODED_SUB}@${ENCODED_ISS} | urlencode.py`


echo ${ENCODED_BOTH}
