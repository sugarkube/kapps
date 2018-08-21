.PHONY: destroy
destroy:
	{ \
		set -e ;\
		if [ "$$APPROVED" = "true" ]; then \
			if [ "$$DEST" != "local" ]; then \
				make tf-destroy ;\
			fi ;\
			make hl-uninstall ;\
		else \
			echo Rerun this task setting 'APPROVED=true' to uninstall this kapp ;\
		fi \
	}
