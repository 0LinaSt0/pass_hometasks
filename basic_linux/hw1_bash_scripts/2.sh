#!/bin/bash


if [[ $# -eq 1 ]] && [[ $1 =~ ^-?[0-9]+$ ]]; then
	if [ $(( $1 % 2 )) -eq 0 ]; then
		echo "The digit is even number"
	else
		echo "The digit is odd number"
	fi
else
	echo "Error: I need one int digit"
 	exit 1
fi