KAPP_ROOT?=$(dir $(PWD))
NAMESPACE?=kube-system
include $(KAPP_ROOT)/common-makefiles/helm/vars.mk
include $(KAPP_ROOT)/common-makefiles/kubectl/vars.mk

.PHONY: install
install:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing kapp... ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) --namespace=$(TILLER_NAMESPACE) \
				apply -f $(TEMPLATED_PATH) ;\
			KUBECONFIG=$(KUBECONFIG) $(HELM) --kube-context=$(KUBE_CONTEXT) \
			  --service-account $(SERVICE_ACCOUNT) \
			  --tiller-namespace $(TILLER_NAMESPACE) \
			  $(TILLER_OPTIONS) \
			  init --wait --upgrade ;\
		else \
			echo Would apply the YAML file at $(TEMPLATED_PATH) with $(KUBECTL) ;\
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}

.PHONY: delete
delete:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Deleting kapp... ;\
			KUBECONFIG=$(KUBECONFIG) $(HELM) --kube-context=$(KUBE_CONTEXT) \
			  --tiller-namespace $(TILLER_NAMESPACE) \
			  reset ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) --namespace=$(TILLER_NAMESPACE) \
				delete $(ROLE_BINDING) $(SERVICE_ACCOUNT) ;\
			KUBECONFIG=$(KUBECONFIG) $(KUBECTL) --context=$(KUBE_CONTEXT) --namespace=$(TILLER_NAMESPACE) \
				delete $(ROLE) $(ROLE_NAME) ;\
		else \
			echo Rerun this task setting 'APPROVED=true' to delete this kapp ;\
		fi \
	}
