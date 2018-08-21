.PHONY: tf-clean
tf-clean:
	@if [ -d "$(TERRAFORM_DIR)" ]; then \
		-rm -rf $(TERRAFORM_DIR)/.terraform ;\
		-rm $(TERRAFORM_DIR)/*.tfplan* ;\
		-rm $(TERRAFORM_DIR)/_generated_* ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
