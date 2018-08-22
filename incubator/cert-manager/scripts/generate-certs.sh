#!/usr/bin/env bash

# Requires cfssl. See https://github.com/cloudflare/cfssl. On OSX install with
# `brew install cfssl`.

set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cert_dir="$script_dir/../_generated_certs"
json_dir="$script_dir/json"

if [ ! -d "$cert_dir" ]; then
  mkdir -p "$cert_dir"
fi

cd $cert_dir
cfssl gencert -initca "$json_dir/ca.json" | cfssljson -bare ca
mv "$cert_dir/ca-key.pem" "$cert_dir/ca.key"
mv "$cert_dir/ca.pem" "$cert_dir/ca.crt"
cd ..
