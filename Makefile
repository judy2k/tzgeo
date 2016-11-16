all: test-release

ensureclean:
	@ if ! git diff-index --quiet HEAD --; then \
		echo You must commit your changes before releasing\! >&2; \
		exit 1; \
	fi

test-release: ensureclean
	python setup.py sdist bdist_wheel upload -r pypitest
	
release: ensureclean
	@echo "Releasing to PRODUCTION in 5 seconds..."
	@sleep 5
	python setup.py sdist bdist_wheel upload -r pypi

.PHONY: ensureclean test-release release
