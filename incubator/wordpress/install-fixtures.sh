#!/bin/bash -ex

KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT -n $NAMESPACE \
  cp ${KAPP_ROOT}/data/data.sql ${RELEASE}-mariadb-0:/tmp/
DB_PASSWORD=$(KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT \
  -n $NAMESPACE get secrets ${RELEASE}-mariadb -o jsonpath="{.data.mariadb-password}" | base64 --decode)
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT -n $NAMESPACE \
  exec ${RELEASE}-mariadb-0 -- bash -c "mysql -u wordpress -p$DB_PASSWORD wordpress < /tmp/data.sql"
