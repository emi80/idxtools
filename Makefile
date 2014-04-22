.PHONY: test

all:
	python setup.py build

devel:
	python setup.py develop

test:
	@echo -n "Running pytest"
	@py.test -q test
	@echo "All tests ran successfully"
