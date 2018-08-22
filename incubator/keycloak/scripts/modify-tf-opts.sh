#!/usr/bin/env bash
#
# Modifies the input parameter to append the database password if it's
# available in the shell. This can allow passing it from e.g. Jenkins into
# terraform.
#
set -e

tf_opts=$1

if [[ ! -z "${KEYCLOAK_DB_PASSWORD}" ]]; then
  tf_opts="$(tf_opts) -var db_password=\"${KEYCLOAK_DB_PASSWORD}\""
fi

echo "$tf_opts"
