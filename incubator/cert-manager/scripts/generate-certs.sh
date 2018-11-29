#!/usr/bin/env bash

# Requires cfssl. See https://github.com/cloudflare/cfssl. On OSX install with
# `brew install cfssl`.
#
# See the cfssl tutorial at: https://coreos.com/os/docs/latest/generate-self-signed-certificates.html

set -e

CFSSL_PATH=$(which cfssl)
CFSSLJSON_PATH=$(which cfssljson)

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cert_dir="$script_dir/../_generated_certs"
json_dir="$script_dir/json"

if [ ! -d "$cert_dir" ]; then
  mkdir -p "$cert_dir"
fi

cd $cert_dir
"$CFSSL_PATH" gencert -initca "$json_dir/ca.json" | "$CFSSLJSON_PATH" -bare ca
mv "$cert_dir/ca-key.pem" "$cert_dir/ca.key"
mv "$cert_dir/ca.pem" "$cert_dir/ca.crt"
cd ..
