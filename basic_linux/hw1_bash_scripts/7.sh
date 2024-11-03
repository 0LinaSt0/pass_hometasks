#!/bin/bash

# I did it for have opportunity to test it on another dirs
if [[ $# -eq 1 ]] && [[ -d $1 ]]; then
    dir_path=$1
else
    dir_path="./"
fi

echo "Files in directory '$dir_path':";
find $dir_path -type f -name "*.txt" -maxdepth 1