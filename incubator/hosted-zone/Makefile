tf-params=-var cluster_name=$(CLUSTER_NAME) \
	-var parent_hosted_zone=$(PARENT_HOSTED_ZONE) \
	-var region=$(REGION)

KAPP_ROOT?=$(dir $(PWD))
include $(KAPP_ROOT)/common-makefiles/default.mk
