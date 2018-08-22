.PHONY: destroy
destroy:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			make tf-destroy ;\
			make hl-uninstall ;\
		else \
			echo Rerun this task setting 'APPROVED=true' to uninstall this kapp ;\
		fi \
	}
