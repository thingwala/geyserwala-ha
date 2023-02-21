setup:
	python -m pip install -r ./requirements_dev.txt

check:
	flake8 ./custom_components/thingwala_geyserwala --ignore E501
	find ./custom_components/thingwala_geyserwala -name '*.py' \
	| xargs pylint -d invalid-name \
	               -d missing-docstring \
	               -d line-too-long \
	               -d import-error \
	               -d no-name-in-module

test:
	pytest ./test/ -vvv --junitxml=./reports/unittest-results.xml
