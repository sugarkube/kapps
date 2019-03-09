.PHONY: hl-install
hl-install: hl-lint
	if [ ! -z "$(KUBE_CONTEXT)" ]; then \
		KUBECONFIG=$(KUBECONFIG) $(HELM) upgrade --kube-context=$(KUBE_CONTEXT) \
			--tiller-namespace=$(TILLER_NAMESPACE)
			--wait --install \
			$(RELEASE) $(CHART_DIR) \
			-f values.yaml \
			--namespace=$(NAMESPACE) \
			--timeout 600 \
			$(helm-params) \
			$(local-helm-opts) ;\
	else \
		echo No KUBE_CONTEXT configured, skipping helm install... ;\
	fi
