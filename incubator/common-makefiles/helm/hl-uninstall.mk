.PHONY: hl-uninstall
hl-uninstall:
	$(HELM) delete --kube-context=$(KUBE_CONTEXT) --purge $(RELEASE)
