helm-params=--set ca.crt=$(CERT_MANAGER_CA_CRT) \
			--set ca.key=$(CERT_MANAGER_CA_KEY)

include ../common-makefiles/default.mk

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
		$(helm_params) \
		$(local_helm_opts) && \
		sed -e 's/{{ chart }}/$(CHART)/g' -e 's/{{ namespace }}/$(NAMESPACE)/g' \
			k8s/clusterissuer.yaml | $(KUBECTL) apply -f -

all:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			if [ -z "$$CERT_MANAGER_CA_CRT" ]; then \
				echo ;\
				echo Generating certs... ;\
				make bootstrap ;\
				. ./scripts/export-certs.sh ;\
			else \
				echo ;\
				echo Secrets already exported to the shell ;\
			fi ;\
			make hl-install ;\
		else \
			echo Nothing to do. Return with 'APPROVED=true' to install ;\
		fi \
	}
