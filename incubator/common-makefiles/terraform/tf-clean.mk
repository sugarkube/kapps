.PHONY: tf-clean
tf-clean:
	if [ -d "$(TERRAFORM_DIR)" ]; then \
		rm -rf $(TERRAFORM_DIR)/.terraform || true ;\
		rm $(TERRAFORM_DIR)/*.tfplan* || true ;\
		rm $(TERRAFORM_DIR)/_generated_* || true ;\
		find $(TERRAFORM_DIR) -name '_generated_*.tfvars' -type f -delete || true ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
