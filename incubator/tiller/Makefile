include ../common-makefiles/helm/vars.mk

.PHONY: install
install:
	$(KUBECTL) apply -f ./k8s/rbac.yaml
	$(HELM) --kube-context=$(KUBE_CONTEXT) --service-account tiller init

.PHONY: all
all:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing kapp... ;\
			echo Installing kapp ;\
			make install ;\
			echo Sleeping to give tiller time to initialise ;\
			sleep 30 ;\
		else \
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}
