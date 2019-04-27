# Only run `terraform init` if it hasn't already been initialised
.PHONY:
tf-refresh:
	{ \
		set -e ;\
		if [ -d "$(TERRAFORM_DIR)" ] && [ ! -z "$(TERRAFORM)" ]; then \
			if [ ! -d "$(TERRAFORM_DIR)/.terraform" ]; then \
			  $(MAKE) tf-init ;\
			  cd $(TERRAFORM_DIR) && $(TERRAFORM) refresh \
			    $(tf-params) \
			    $(local-tf-opts) && \
			    cd .. ;\
			else \
			  echo "Terraform already initialised - won't refresh output" ;\
			fi ;\
		else \
		echo [$@] No $(TERRAFORM_DIR) directory or blank TERRAFORM path, skipping... ;\
		fi \
	}
