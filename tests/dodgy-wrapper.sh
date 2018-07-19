#!/usr/bin/env sh
dodgy_output="$(dodgy "$@")"
echo "$dodgy_output"
[ "$(wc -l <<< "$dodgy_output")" -eq 3 ]
