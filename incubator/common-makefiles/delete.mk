.PHONY: delete
delete:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			make hl-uninstall ;\
			make tf-destroy ;\
		else \
			echo Rerun this task setting 'APPROVED=true' to uninstall this kapp ;\
		fi \
	}
