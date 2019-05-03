.PHONY: hl-lint
hl-lint:
	if [ ! -z "$(KUBE_CONTEXT)" ] && [ ! -z "$(HELM)" ] && [ -f "$(CHART_DIR)/Chart.yaml" ]; then \
		KUBECONFIG=$(KUBECONFIG) $(HELM) lint --kube-context=$(KUBE_CONTEXT) \
			$(CHART_DIR) \
			-f values.yaml \
			--namespace=$(NAMESPACE) \
			$(helm-params) \
			$(local-helm-opts) ;\
	else \
		echo "No KUBE_CONTEXT configured, blank HELM path or couldn't find Chart.yaml. Skipping helm lint..." ;\
	fi
