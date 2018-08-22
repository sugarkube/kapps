.PHONY: install
install:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing kapp... ;\
			echo ;\
			if [ "$$PROVIDER" != "local" ]; then \
				echo Applying terraform plan... ;\
				make tf-apply ;\
			fi ;\
			echo Installing helm chart ;\
			make hl-install ;\
		else \
			if [ "$$PROVIDER" != "local" ]; then \
				echo Planning terraform changes... ;\
				make tf-plan ;\
			fi ;\
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}
