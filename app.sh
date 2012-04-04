#!/bin/bash

vflag=off

if [[ $1 == "--help" ]] 
then
    echo "usage: $0"
    exit 0
fi

echo -n "Starting API Server..."
python $PWD/server.py > $PWD/logs/api.log 2>&1 &
echo "done"

echo -n "Starting Node Frontend..."
node $PWD/frontend/app.js > $PWD/logs/node.log 2>&1 &
echo "done"

trap "kill 0; exit 0" INT

wait