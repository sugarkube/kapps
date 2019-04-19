.PHONY: tf-output
tf-output:
	if [ ! -z "$(tf-output)" ]; then \
		cd $(TERRAFORM_DIR) && $(TERRAFORM) output -json > $(tf-output) && cd .. ;\
	else \
		echo [$@] No need to save terraform output... ;\
	fi
