helm-params=--set keycloak.keycloak.ingress.hosts={$(RELEASE).$(HOSTED_ZONE)}
tf-params=-var hosted_zone=$(HOSTED_ZONE)

KAPP_ROOT?=..
include $(KAPP_ROOT)/common-makefiles/default.mk
