.PHONY: hl-uninstall
hl-uninstall:
	{ \
		if [ ! -z "$(KUBE_CONTEXT)" ] && [ ! -z "$(HELM)" ] && [ -f "$(CHART_DIR)/Chart.yaml" ]; then \
			EXISTS="$$(KUBECONFIG=$(KUBECONFIG) $(HELM) list \
								--tiller-namespace=$(TILLER_NAMESPACE) \
								--kube-context=$(KUBE_CONTEXT) $(RELEASE))" ;\
			if [ -z "$$EXISTS" ]; then \
				echo "Couldn't find an installed helm chart called '$(RELEASE)'. Won't run helm uninstall." ;\
			else \
				if [ ! -z "$(KUBE_CONTEXT)" ] && [ ! -z "$(HELM)" ]; then \
					KUBECONFIG=$(KUBECONFIG) $(HELM) delete \
						--tiller-namespace=$(TILLER_NAMESPACE) \
						--kube-context=$(KUBE_CONTEXT) --purge $(RELEASE) ;\
				else \
			echo No KUBE_CONTEXT configured, blank HELM path or couldn't find Chart.yaml. Skipping helm uninstall... ;\
				fi \
			fi \
		fi \
	}
