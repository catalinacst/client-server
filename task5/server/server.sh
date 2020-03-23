#!/bin/bash

mkdir $2/
python3.7 server.py $1 $2 $3 $4
rm -r $2/
rm info_$2