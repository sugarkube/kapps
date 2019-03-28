.PHONY: clean
clean: tf-clean
	-rm *.log
	-rm *.err
	-find . -name '_generated_*' -type f -delete
	-find . -name '_generated_*' -type d -exec rm -r {} ';'
