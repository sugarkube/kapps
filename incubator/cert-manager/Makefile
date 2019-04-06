KAPP_ROOT?=$(dir $(PWD))
include $(KAPP_ROOT)/common-makefiles/default.mk

.PHONY: install
install:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing CRDs and creating the namespace... ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) \
				apply -f ./k8s/00-crds.yaml ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) \
				apply -f $(TEMPLATED_PATH) ;\
			make hl-install ;\
		else \
			make hl-lint ;\
			echo Rerun with 'APPROVED=true' to install ;\
		fi \
	}

.PHONY: delete
delete:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			make hl-uninstall ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) \
				delete --now namespace $(NAMESPACE) ;\
		else \
			make hl-lint ;\
			echo Rerun with 'APPROVED=true' to install ;\
		fi \
	}
