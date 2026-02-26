.PHONY: install dev test build clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info/
