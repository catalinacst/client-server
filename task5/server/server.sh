#!/bin/bash

mkdir $2/
mkdir info_server/
python3.7 server.py $1 $2 $3 $4
rm -r $2/
rm -r info_server/