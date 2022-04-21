
ISORT_PARAMS = --trailing-comma --use-parentheses --line-width=88
BLACK_PARAMS = -t py39

.PHONY: format-check format pylint pyright test

format-check:
	(isort $(ISORT_PARAMS) --check-only .) && (black $(BLACK_PARAMS) --check .)

format:
	isort $(ISORT_PARAMS) .
	black $(BLACK_PARAMS) .

pylint: format-check
	pylint src/* tests/*

pyright: pylint
	pyright

test:
	python -m pytest tests
