#!/bin/bash

mkdir recv_$2/
python3.7 client.py $1 $2 $3 $4
rm -r recv_$2/