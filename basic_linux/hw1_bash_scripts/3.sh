#!/bin/bash

if [[ $# -eq 2 ]]; then
	s_num=$1
	filepath=$2
	if [[ $s_num =~ ^[0-9]+$ ]]; then
		if [[ -f $filepath ]]; then
			s_count=$(wc -l < $filepath)

			if [[ $s_num -gt 0 ]] && [[ $s_num -le $s_count ]]; then
				head -n $s_num $filepath | tail -n 1
			else
				echo "Error: the file doesn't have the strind $s_num"
			fi
		else
			echo "Error: file not found"
		fi
	else
		echo "Error: I expect positive int digit in first argument"
	fi
else
	echo "Error: I need two arguments - the string number and path to file"
fi
