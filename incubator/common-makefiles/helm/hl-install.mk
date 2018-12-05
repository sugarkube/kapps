.PHONY: hl-install
hl-install: hl-lint
	$(HELM) upgrade --kube-context=$(KUBE_CONTEXT) --wait --install \
		$(RELEASE) $(CHART_DIR) \
		-f values.yaml \
		--namespace=$(NAMESPACE) \
		--timeout 600 \
		$(helm-params) \
		$(local-helm-opts)
