SHELL=/bin/bash

# default make target
include $(KAPP_ROOT)/common-makefiles/help.mk

# kubectl vars
include $(KAPP_ROOT)/common-makefiles/kubectl/vars.mk

# helm targets
include $(KAPP_ROOT)/common-makefiles/helm/vars.mk
include $(KAPP_ROOT)/common-makefiles/helm/hl-install.mk
include $(KAPP_ROOT)/common-makefiles/helm/hl-lint.mk
include $(KAPP_ROOT)/common-makefiles/helm/hl-uninstall.mk

# terraform targets
include $(KAPP_ROOT)/common-makefiles/terraform/vars.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-apply.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-clean.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-destroy.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-fmt.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-init.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-plan.mk
include $(KAPP_ROOT)/common-makefiles/terraform/tf-validate.mk

# Top-level targets. Some of these depend on the ones above.
include $(KAPP_ROOT)/common-makefiles/install.mk
include $(KAPP_ROOT)/common-makefiles/post-install.mk
include $(KAPP_ROOT)/common-makefiles/clean.mk
include $(KAPP_ROOT)/common-makefiles/destroy.mk
