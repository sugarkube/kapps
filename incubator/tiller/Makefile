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
			echo Installing kapp ;\
			sed 's/{{namespace}}/$(NAMESPACE)/g' ./k8s/rbac.yaml | $(KUBECTL) apply -f - ;\
			$(HELM) --kube-context=$(KUBE_CONTEXT) \
			  --service-account tiller \
			  init --wait --upgrade;\
		else \
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}
