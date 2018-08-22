.PHONY: install
install:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			echo Approved. Installing kapp... ;\
			echo ;\
			make tf-apply ;\
			echo Installing helm chart ;\
			make hl-install ;\
		else \
			make tf-plan ;\
			echo Rerun this task setting 'APPROVED=true' to install this kapp ;\
		fi \
	}
