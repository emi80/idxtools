.PHONY: test

all:
	python setup.py build

devel:
	python setup.py develop

test:
	@py.test test --maxfail=1
