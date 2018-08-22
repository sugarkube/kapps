#!/usr/bin/env bash
#
# Exports certs to the shell
#
set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cert_dir="$script_dir/certs"

export RDS_CA_CRT=$(base64 -i "$cert_dir/rds-ca-2015-root.pem")
