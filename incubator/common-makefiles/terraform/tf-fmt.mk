.PHONY: tf-fmt
tf-fmt: tf-init
	@if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd $(TERRAFORM_DIR) && $(TERRAFORM) fmt && cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
