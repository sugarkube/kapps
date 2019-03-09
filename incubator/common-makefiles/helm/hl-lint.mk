.PHONY: hl-lint
hl-lint:
	if [ ! -z "$(KUBE_CONTEXT)" ]; then \
		KUBECONFIG=$(KUBECONFIG) $(HELM) lint --kube-context=$(KUBE_CONTEXT) \
			$(CHART_DIR) \
			-f values.yaml \
			--namespace=$(NAMESPACE) \
			$(helm-params) \
			$(local-helm-opts) ;\
	else \
		echo No KUBE_CONTEXT configured, skipping helm lint... ;\
	fi
