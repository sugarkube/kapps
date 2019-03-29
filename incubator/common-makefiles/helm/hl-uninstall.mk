.PHONY: hl-uninstall
hl-uninstall:
	exists=$(KUBECONFIG=$(KUBECONFIG) $(HELM) list \
             			--tiller-namespace=$(TILLER_NAMESPACE) \
             			--kube-context=$(KUBE_CONTEXT) $(RELEASE)) ;\
    if [ -z "$(exists)" ]; then \
    	echo Couldn't find an installed helm chart called $(RELEASE). Won't run helm uninstall. ;\
    else \
		if [ ! -z "$(KUBE_CONTEXT)" ]; then \
			KUBECONFIG=$(KUBECONFIG) $(HELM) delete \
				--tiller-namespace=$(TILLER_NAMESPACE) \
				--kube-context=$(KUBE_CONTEXT) --purge $(RELEASE) ;\
		else \
			echo No KUBE_CONTEXT configured, skipping helm uninstall... ;\
		fi \
	fi
