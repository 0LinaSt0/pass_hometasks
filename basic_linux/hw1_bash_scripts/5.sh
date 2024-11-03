#!/bin/bash

materials_path="./tmp_sources/"

filepath1=$materials_path"file1.txt"
filepath2=$materials_path"file2.txt"
filepath3=$materials_path"file3.txt"

target_filepath=$materials_path"combined.txt"

if [[ -f $filepath1 ]] && [[ -f $filepath2 ]] && [[ -f $filepath3 ]]; then
    cat $filepath1 > $target_filepath;
    cat $filepath2 >> $target_filepath;
    cat $filepath3 >> $target_filepath
else
    echo "Error: some of files doesn't exists"
fi