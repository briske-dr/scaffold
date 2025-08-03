install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

format:
	black *.py

lint:
	pylint --disable=R,C $(shell find . -name "*.py")

test:
	python -m pytest -vv --cov --cov-config=.coveragerc --cov-report=term

all: install format lint test
