#!/usr/bin/env bash
#
# Exports terraform output as environment variables.
#

set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
TERRAFORM=$(which terraform)

echo Exporting terraform output to env vars...
cd "$script_dir"
$(${TERRAFORM} output -json | jq -r 'to_entries[] | [(.key|ascii_upcase), .value.value] | "export \(.[0])=\(.[1])"')
cd ..
