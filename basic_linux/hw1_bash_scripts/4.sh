#!/bin/bash

if [[ $# -eq 1 ]]; then
    if [[ -d $1 ]]; then
        find $1 -type f -mtime +5 -ls -maxdepth 1 -exec rm -rf {} +
    else
        echo "Error: directory not found"
    fi
else
    echo "Error: I need an argumen - the path directory"
fi