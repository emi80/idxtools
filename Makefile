all:
	python setup.py build

devel:
	python setup.py develop

test:
	@echo -n "Running pytest"
	@py.test -q test_index.py
	@echo "All tests ran successfully"
