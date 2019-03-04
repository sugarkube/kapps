.PHONY: tf-apply
tf-apply:
	if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd $(TERRAFORM_DIR) && $(TERRAFORM) apply $(local-tf-opts) plan.out && cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
