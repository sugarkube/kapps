.PHONY: tf-validate
tf-validate: tf-fmt
	@if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd $(TERRAFORM_DIR) && $(TERRAFORM) validate \
		  $(tf-params)\
		  $(local-tf-opts) \
		&& cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
