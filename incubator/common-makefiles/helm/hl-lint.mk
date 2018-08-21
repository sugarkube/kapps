.PHONY: hl-lint
hl-lint:
	$(HELM) lint --kube-context=$(KUBE_CONTEXT) \
		. \
		-f values.yaml \
		--namespace=$(NAMESPACE) \
		$(helm-params) \
		$(local-helm-opts)
