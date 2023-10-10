.PHONY: install format format-check isort isort-check lint \
	mypy test check-all clean build dist wheel upload

install:
	pip3 install --upgrade pip
	pip3 install -r tests/requirements.txt
	pip3 install -r requirements.ci.txt

format:
	black flask_docs tests examples

format-check:
	black flask_docs tests examples --check

isort:
	isort flask_docs tests examples --profile black

isort-check:
	isort flask_docs tests examples --profile black --check

lint:
	flake8 flask_docs tests examples

mypy:
	mypy flask_docs tests examples

test:
	pytest \
		--cov flask_docs \
		--cov-config .coveragerc \
		--cov-report xml \
		--junit-xml results.xml \
		-vv tests
	coverage report -m --skip-covered

check-all: format-check isort-check lint mypy test

clean:
	rm -rf build dist

build: clean
	python3 setup.py build

dist: clean
	python3 setup.py sdist

wheel: clean
	python3 setup.py bdist_wheel

upload:
	twine upload dist/*
