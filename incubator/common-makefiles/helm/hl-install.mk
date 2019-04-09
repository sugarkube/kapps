.PHONY: hl-install
hl-install: hl-lint
	if [ ! -z "$(KUBE_CONTEXT)" ] && [ ! -z "$(HELM)" ]; then \
		echo Installing helm chart... ;\
		KUBECONFIG=$(KUBECONFIG) $(HELM) upgrade --kube-context=$(KUBE_CONTEXT) \
			--tiller-namespace=$(TILLER_NAMESPACE) \
			--wait --install \
			$(RELEASE) $(CHART_DIR) \
			--namespace=$(NAMESPACE) \
			--timeout 600 \
			$(helm-params) \
			$(local-helm-opts) ;\
	else \
		echo No KUBE_CONTEXT configured or blank HELM path. Skipping helm install... ;\
	fi
