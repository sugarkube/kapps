KUBECTL?=$(shell which kubectl)
HELM?=$(shell which helm)

CHART=$(shell basename `pwd`)
CHART_DIR?=.
NAMESPACE?=$(CHART)
RELEASE?=$(CHART)
KUBE_CONTEXT?=$(shell "$(KUBECTL)" config current-context)

helm-opts?=
# this can be overridden to modify it, e.g. to add extra flags, etc.
local-helm-opts?=$(helm-opts)
