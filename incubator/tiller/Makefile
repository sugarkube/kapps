include ../common-makefiles/helm/vars.mk

.PHONY: install
install:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing kapp... ;\
			echo Installing kapp ;\
			$(KUBECTL) apply -f ./k8s/rbac.yaml ;\
			$(HELM) --kube-context=$(KUBE_CONTEXT) \
			  --service-account tiller \
			  init --wait --upgrade;\
		else \
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}
