.PHONY: clean
help:
	@echo To install standard kapps, run \"make install\" with the following env vars:
	@echo
	@echo Mandatory env vars:
	@echo APPROVED=\<false/true\> - Run first with \'APPROVED=false\' to plan then \'APPROVED=true\' to actually install.
	@echo
	@echo Optional env vars:
	@echo PROFILE=\<profile\>
	@echo CLUSTER=\<cluster\>
	@echo CLUSTER_PROFILE=\<cluster_profile\>
	@echo REGION=\<region\>
	@echo KUBE_CONTEXT=\<context\>
	@echo NAMESPACE=\<namespace\>
	@echo RELEASE=\<release\>
	@echo
	@echo To delete, run \"make destroy\".
