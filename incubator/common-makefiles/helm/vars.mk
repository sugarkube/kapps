RUN_HELM?=true
HELM?=$(shell which helm)

CHART=$(shell basename `pwd`)
CHART_DIR?=.
NAMESPACE?=$(CHART)
RELEASE?=$(CHART)
TILLER_NAMESPACE?=kube-system

helm-opts?=
# this can be overridden to modify it, e.g. to add extra flags, etc.
local-helm-opts?=$(helm-opts)
