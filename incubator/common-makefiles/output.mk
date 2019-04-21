# This target should just write output for the kapp to a file without causing any side effects
.PHONY: output
output:
	$(MAKE) tf-output
