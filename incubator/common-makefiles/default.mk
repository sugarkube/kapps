SHELL=/bin/bash
ENABLED?=true

# default make target
include $(KAPP_ROOT)/common-makefiles/help.mk

# kubectl vars
include $(KAPP_ROOT)/common-makefiles/kubectl/vars.mk

# helm targets. Only run Helm if it's enabled
include $(KAPP_ROOT)/common-makefiles/helm/vars.mk
ifeq ($(RUN_HELM),true)
include $(KAPP_ROOT)/common-makefiles/helm/hl-install.mk
include $(KAPP_ROOT)/common-makefiles/helm/hl-lint.mk
include $(KAPP_ROOT)/common-makefiles/helm/hl-uninstall.mk
else
$(info RUN_HELM variable is not 'true'. Helm won't be run.)
# no-op targets so make doesn't output errors
hl-lint:
hl-install:
hl-uninstall:
endif

# terraform targets. Only run Terraform if there's a path to the binary
include $(KAPP_ROOT)/common-makefiles/terraform/vars.mk
ifeq ($(RUN_TERRAFORM),true)
include $(KAPP_ROOT)/common-makefiles/terraform/tf-apply.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-clean.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-destroy.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-fmt.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-init.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-plan.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-validate.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-output.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-refresh.mk
else
$(info RUN_TERRAFORM variable is not 'true'. Terraform won't be run.)
# no-op targets so make doesn't output errors
tf-apply:
tf-plan:
tf-destroy:
tf-output:
endif

# Top-level targets. Some of these depend on the ones above.
ifeq ($(ENABLED),true)
include $(KAPP_ROOT)/common-makefiles/install.mk
include $(KAPP_ROOT)/common-makefiles/pre-install.mk
include $(KAPP_ROOT)/common-makefiles/post-install.mk
include $(KAPP_ROOT)/common-makefiles/clean.mk
include $(KAPP_ROOT)/common-makefiles/delete.mk
include $(KAPP_ROOT)/common-makefiles/output.mk
else
install:
delete:
output:
endif