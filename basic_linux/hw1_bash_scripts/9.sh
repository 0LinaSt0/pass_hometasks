#!/bin/bash


# I did it for have opportunity to test it on another dirs
if [[ $# -eq 1 ]] && [[ -d $1 ]]; then
    dir_path=$1
else
    dir_path="./"
fi


for obj in $dir_path/*; do
    if [[ -f $obj ]]; then
        filename="${obj%.*}" # all before last dot
        extension="${obj##*.}" # all after last dot

        mv $obj $filename"_backup."$extension
    fi
done
