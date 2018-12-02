KAPP_ROOT?=$(dir $(PWD))
include $(KAPP_ROOT)/common-makefiles/default.mk

# maria DB seems to do something funky which means we can't just pull the value from the secret
post-install:
	{ \
		set -e ;\
		if [ "$(PROFILE)" == "local" ]; then \
			kubectl -n $(NAMESPACE) cp $(KAPP_ROOT)/data/data.sql $(NAMESPACE)-mariadb-0:/tmp/ ;\
			POD=$$(kubectl -n $(NAMESPACE) get pod -l app=$(NAMESPACE)-$(CHART) -o jsonpath="{.items[0].metadata.name}") ;\
			DB_PASSWORD=$$(kubectl -n $(NAMESPACE) exec -it $$POD -- bash -c "env | grep WORDPRESS_DATABASE_PASSWORD | sed -e 's/.*=//' | tr -d '\n'") ;\
			kubectl -n $(NAMESPACE) exec $(NAMESPACE)-mariadb-0 -- bash -c "mysql -u wordpress -p$$DB_PASSWORD wordpress < /tmp/data.sql" ;\
		fi ;\
    }