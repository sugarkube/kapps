.PHONY: hl-install
hl-install:
	$(HELM) upgrade --kube-context=$(KUBE_CONTEXT) --wait --install \
		$(RELEASE) . \
		-f values.yaml \
		--namespace=$(NAMESPACE) \
		$(helm-params) \
		$(local-helm-opts)
