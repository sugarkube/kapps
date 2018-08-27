#!/usr/bin/env bash

# Requires cfssl. See https://github.com/cloudflare/cfssl. On OSX install with
# `brew install cfssl`.

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
"$CFSSL_PATH" gencert -ca="$cert_dir/ca.pem" -ca-key="$cert_dir/ca-key.pem" "$json_dir/server.json" | "$CFSSLJSON_PATH" -bare server
"$CFSSL_PATH" gencert -ca="$cert_dir/ca.pem" -ca-key="$cert_dir/ca-key.pem" "$json_dir/agent.json" | "$CFSSLJSON_PATH" -bare agent
cd ..
