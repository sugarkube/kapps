helm-params=--set ca.crt=$(CERT_MANAGER_CA_CRT) \
			--set ca.key=$(CERT_MANAGER_CA_KEY)

KAPP_ROOT?=$(dir $(PWD))
include $(KAPP_ROOT)/common-makefiles/default.mk

bootstrap:
	{ \
		set -e ;\
		cd ./scripts ;\
		./generate-certs.sh ;\
		cd .. ;\
		echo ;\
		echo "Certs generated. Use them with '. ./scripts/export-certs.sh && make hl-install'" ;\
	}

hl-install: hl-lint
	helm upgrade --kube-context=$(KUBE_CONTEXT) --wait --install \
		$(RELEASE) . \
		--namespace=$(NAMESPACE) \
		$(helm-params) \
		$(local-helm-opts) && \
		$(KUBECTL) apply -f ./k8s/clusterissuer.yaml

install:
	{ \
		set -e ;\
		if [ -z "$$CERT_MANAGER_CA_CRT" ]; then \
			echo ;\
			echo Generating certs... ;\
			make bootstrap ;\
			. ./scripts/export-certs.sh ;\
		else \
			echo ;\
			echo Secrets already exported to the shell ;\
		fi ;\
		if [ "$$APPROVED" = "true" ]; then \
			make hl-install ;\
		else \
			make hl-lint ;\
			echo Rerun with 'APPROVED=true' to install ;\
		fi \
	}
