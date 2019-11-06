#!/bin/bash

python3 setup.py sdist build && \
python3 setup.py bdist_wheel --universal && \
twine upload dist/*