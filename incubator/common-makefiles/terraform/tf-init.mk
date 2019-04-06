# Only run `terraform init` if it hasn't already been initialised
.PHONY: tf-init
tf-init:
	{ \
		set -e ;\
		if [ -d "$(TERRAFORM_DIR)" ] && [ ! -z "$(TERRAFORM)" ]; then \
			if [ ! -d "$(TERRAFORM_DIR)/.terraform" ]; then \
			  cd $(TERRAFORM_DIR) && $(TERRAFORM) init && cd .. ;\
			else \
			  echo "Terraform already initialised" ;\
			fi ;\
		else \
		echo [$@] No $(TERRAFORM_DIR) directory or blank TERRAFORM path, skipping... ;\
		fi \
	}
