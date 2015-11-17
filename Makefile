.PHONY: all test

all: test

test:
	py.test

clean: clean-pyc

clean-pyc:
	@find . -name '*.pyc' -exec rm {} \;
	@find . -name '__pycache__' -type d | xargs rm -rf

develop:
	@pip install --editable .

tox-test:
	@tox

.PHONY: test all clean clean-pyc develop tox-test
