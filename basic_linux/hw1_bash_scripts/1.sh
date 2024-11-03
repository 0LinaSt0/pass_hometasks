#!/bin/bash

error_log="Error: I need two digits for calculating"

float_int_pattern="^-?[0-9]+(\.[0-9]+)?$"

if [ $# -ne 2 ]; then
	echo $error_log
	exit 1
fi

num_a=$1
num_b=$2

if ! [[ $num_a =~ $float_int_pattern ]] || ! [[ $num_b =~ $float_int_pattern ]]; then
	echo $error_log
	exit 1
fi

sum=$(echo "$num_a + $num_b" | bc)

echo $sum

