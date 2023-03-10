.PHONY: install lint format format-check isort isort-check mypy test test-all clean dist build wheel upload

install:
	pip3 install --upgrade pip
	pip3 install -r tests/requirements.txt
	pip3 install -r requirements.ci.txt

lint:
	flake8 flask_docs tests examples

format:
	black flask_docs tests examples

format-check:
	black flask_docs tests examples --check

isort:
	isort flask_docs tests examples --profile black

isort-check:
	isort flask_docs tests examples --profile black --check

mypy:
	mypy flask_docs tests examples

test:
	pytest -vv --cov=flask_docs --cov-config .coveragerc --cov-report=xml --junit-xml results.xml tests
	coverage report -m --skip-covered

test-all: lint format-check isort-check mypy test

clean:
	rm -rf dist build

dist: clean
	python3 setup.py sdist

build: clean
	python3 setup.py build

wheel: clean
	python3 setup.py bdist_wheel

upload:
	twine upload dist/*