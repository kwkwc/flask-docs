.PHONY: install lint mypy format isort test clean dist build wheel upload

install:
	pip3 install -r tests/requirements.txt
	pip3 install -r requirements.ci.txt

lint:
	flake8 flask_docs tests examples

mypy:
	mypy flask_docs tests examples

format:
	black flask_docs tests examples --check

isort:
	isort flask_docs tests examples --profile black --check

test: mypy
test: format
test: isort
test: lint
	pytest --cov=flask_docs --cov-report=xml

clean:
	rm -rf dist build

dist: clean
	python3 setup.py sdist

build: clean
	python3 setup.py build

wheel: clean
	python3 setup.py bdist_wheel --universal

upload:
	twine upload dist/*
