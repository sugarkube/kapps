.PHONY: clean
clean: tf-clean
	-rm *.log
	-rm *.err
	-find . -name '_generated_*' -delete
