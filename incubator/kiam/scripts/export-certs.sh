#!/usr/bin/env bash
#
# Exports certs to the shell
#
set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cert_dir="$script_dir/../_generated_certs"

export KIAM_CA_PEM=$(base64 -i "$cert_dir/ca.pem")
export KIAM_SERVER_PEM=$(base64 -i "$cert_dir/server.pem")
export KIAM_SERVER_KEY=$(base64 -i "$cert_dir/server-key.pem")
export KIAM_AGENT_PEM=$(base64 -i "$cert_dir/agent.pem")
export KIAM_AGENT_KEY=$(base64 -i "$cert_dir/agent-key.pem")
