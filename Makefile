SHELL=/bin/bash

.PHONY: install
install:
	pip3 install --upgrade pip
	pip3 install -r tests/requirements.txt
	pip3 install -r requirements.ci.txt

.PHONY: format
format:
	black flask_docs tests examples

.PHONY: format-check
format-check:
	black flask_docs tests examples --check

.PHONY: isort
isort:
	isort flask_docs tests examples --profile black

.PHONY: isort-check
isort-check:
	isort flask_docs tests examples --profile black --check

.PHONY: lint
lint:
	flake8 flask_docs tests examples

.PHONY: mypy
mypy:
	mypy flask_docs tests examples

.PHONY: test
test:
	pytest \
		--cov flask_docs \
		--cov-config .coveragerc \
		--cov-report xml \
		--junit-xml results.xml \
		-vv tests
	coverage report -m --skip-covered

.PHONY: check-all
check-all: format-check isort-check lint mypy test

.PHONY: clean
clean:
	rm -rf build dist

.PHONY: build
build: clean
	python3 setup.py build

.PHONY: dist
dist: clean
	python3 setup.py sdist

.PHONY: wheel
wheel: clean
	python3 setup.py bdist_wheel

.PHONY: upload
upload:
	twine upload dist/*
