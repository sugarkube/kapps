#!/usr/bin/env bash
#
# Exports certs to the shell
#
set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cert_dir="$script_dir/../_generated_certs"

export CERT_MANAGER_CA_CRT=$(base64 -i "$cert_dir/ca.crt")
export CERT_MANAGER_CA_KEY=$(base64 -i "$cert_dir/ca.key")
