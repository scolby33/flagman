#!/usr/bin/env sh
dodgy_output="$(dodgy "$@")"
echo "$dodgy_output"
[ "$(wc -l << EOF
"$dodgy_output"
EOF
)" -eq 3 ]
