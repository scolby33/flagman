#!/usr/bin/env sh
pyroma_output="$(pyroma "$@")"
echo "$pyroma_output"
rating="$(sed -Ene 's/^Final rating: ([[:digit:]]{1,2})\/10/\1/p' <<< "$pyroma_output")"
[ "$rating" -eq 10 ]
