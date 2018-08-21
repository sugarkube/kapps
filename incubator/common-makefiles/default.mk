SHELL=/bin/bash

# helm targets
include ../common-makefiles/helm/vars.mk
include ../common-makefiles/helm/hl-install.mk
include ../common-makefiles/helm/hl-lint.mk
include ../common-makefiles/helm/hl-uninstall.mk

# terraform targets
include ../common-makefiles/terraform/vars.mk
include ../common-makefiles/terraform/tf-apply.mk
include ../common-makefiles/terraform/tf-clean.mk
include ../common-makefiles/terraform/tf-destroy.mk
include ../common-makefiles/terraform/tf-fmt.mk
include ../common-makefiles/terraform/tf-init.mk
include ../common-makefiles/terraform/tf-plan.mk
include ../common-makefiles/terraform/tf-validate.mk

# Top-level targets. Some of these depend on the ones above.
include ../common-makefiles/install.mk
include ../common-makefiles/bootstrap.mk
include ../common-makefiles/clean.mk
include ../common-makefiles/destroy.mk
include ../common-makefiles/help.mk
