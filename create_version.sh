#!/bin/bash
git tag -a "v$1" -m "Version $1"
git push --tags
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload -r testpypi dist/*
