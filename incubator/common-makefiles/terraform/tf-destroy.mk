.PHONY: tf-destroy
tf-destroy:
	if [ -d "$(TERRAFORM_DIR)" ]; then \
		cd $(TERRAFORM_DIR) && \
			$(TERRAFORM) destroy -auto-approve $(tf-params) $(local-tf-opts) && \
			cd .. ;\
	else \
		echo [$@] No $(TERRAFORM_DIR) directory, skipping... ;\
	fi
