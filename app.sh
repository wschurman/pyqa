#!/bin/bash

vflag=off

if [[ $1 == "--help" ]] 
then
    echo "usage: $0"
    exit 0
fi

python $PWD/server.py > $PWD/logs/api.log 2>&1 &
#celeryd > $PWD/logs/celeryd.log 2>&1 &
node $PWD/frontend/app.js > $PWD/logs/node.log 2>&1 &

trap "kill 0; exit 0" INT

wait