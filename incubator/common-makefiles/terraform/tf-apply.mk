.PHONY: tf-apply
tf-apply:
	if [ -d "$(TERRAFORM_DIR)" ] && [ ! -z "$(TERRAFORM)" ]; then \
		cd $(TERRAFORM_DIR) && $(TERRAFORM) apply $(local-tf-opts) _generated_plan.tfplan && cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory or blank TERRAFORM path, skipping... ;\
	fi
