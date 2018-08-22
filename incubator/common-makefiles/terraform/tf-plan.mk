.PHONY: tf-plan
tf-plan: tf-validate
	@if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd $(TERRAFORM_DIR) ;\
		$(TERRAFORM) plan -refresh=true -out plan.out \
		  $(tf-params)\
		  $(local-tf-opts) ;\
		cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
