.PHONY: clean
help:
	@echo To install standard kapps, run \"make install\" with the following env vars:
	@echo
	@echo Mandatory env vars:
	@echo \* APPROVED=\<false/true\> - Run first with \'APPROVED=false\' to plan then \'APPROVED=true\' to actually install.
	@echo
	@echo Optional env vars (most have default values):
	@echo \* CLUSTER=\<cluster\> - name of your target cluster
	@echo \* CLUSTER_PROFILE=\<cluster_profile\> - name of your stack cluster profile
	@echo
	@echo Provider-dependent:
	@echo \* REGION=\<region\>
	@echo
	@echo Helm-specific:
	@echo \* KUBE_CONTEXT=\<context\> - Name of the kube context to use
	@echo \* NAMESPACE=\<namespace\> - Helm namespace to install into
	@echo \* RELEASE=\<release\> - Helm release name
	@echo \* CHART_DIR=\<chart_dir\> - to run against charts in relative directories
	@echo
	@echo Terraform-specific:
	@echo \* CLOUD=\<cloud\> - e.g. \'aws\', or \'gcp\' or whatever you have \'terraform_\<cloud\>\' directories for.
	@echo \* TERRAFORM_DIR=\<dir\> - to run terraform against relative dirs. Makes \'CLOUD\' have no effect.
	@echo
	@echo To delete, run \"make destroy\".
