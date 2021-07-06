SHELL = bash

all: install_dev isort isort_check lint test
check: install_dev isort_check lint test

install_dev:
	@pip install -e .[dev] >/dev/null 2>&1

isort:
	@isort -s venv -s venv_py -s .tox -rc --atomic .

isort_check:
	@isort -rc -s venv -s venv_py -s .tox -c .

lint:
	@flake8

test:
	@tox

testcov:
	pytest --cov=jycm --cov-report term-missing

clean:
	@rm -rf .pytest_cache .tox bytedjycm.egg-info
	@rm -rf tests/*.pyc tests/__pycache__

autodocs:
	cd docs && sphinx-apidoc -f -o source/ ../jycm && make html && cd ../

docs:
	cd docs && make html && cd ../

.IGNORE: install_dev
.PHONY: all check install_dev isort isort_check lint test docs
