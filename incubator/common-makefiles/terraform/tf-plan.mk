.PHONY: tf-plan
tf-plan: tf-validate
	if [ -d "$(TERRAFORM_DIR)" ] && [ ! -z "$(TERRAFORM)" ]; then \
		cd $(TERRAFORM_DIR) && \
		$(TERRAFORM) plan -refresh=true -out _generated_plan.tfplan \
		  $(tf-params)\
		  $(local-tf-opts) && \
		cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory or blank TERRAFORM path, skipping... ;\
	fi
