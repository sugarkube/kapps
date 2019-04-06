helm-params=--set nginx-ingress.controller.ingressClass=$(HOSTNAME) \
	--set nameOverride=$(RELEASE)

KAPP_ROOT?=$(dir $(PWD))
include $(KAPP_ROOT)/common-makefiles/default.mk

post-install:
	{ \
		set -e ;\
		if [ "$(PROFILE)" == "local" ]; then \
			echo "Sleeping before populating database..." ;\
			sleep 60 ;\
			kubectl -n $(NAMESPACE) cp $(KAPP_ROOT)/data/data.sql $(RELEASE)-mariadb-0:/tmp/ ;\
			DB_PASSWORD=$$(kubectl -n $(NAMESPACE) get secrets $(RELEASE)-mariadb -o jsonpath="{.data.mariadb-password}" | base64 --decode) ;\
			kubectl -n $(NAMESPACE) exec $(RELEASE)-mariadb-0 -- bash -c "mysql -u wordpress -p$$DB_PASSWORD wordpress < /tmp/data.sql" ;\
		fi ;\
    }