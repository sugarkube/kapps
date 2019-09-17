#!/bin/bash -ex
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT delete crd prometheuses.monitoring.coreos.com
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT delete crd prometheusrules.monitoring.coreos.com
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT delete crd servicemonitors.monitoring.coreos.com
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT delete crd podmonitors.monitoring.coreos.com
KUBECONFIG=$KUBECONFIG $KUBECTL --context=$KUBE_CONTEXT delete crd alertmanagers.monitoring.coreos.com
