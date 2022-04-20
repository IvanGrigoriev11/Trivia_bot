
.PHONY: format-check format pylint pyright test

format-check:
	(isort -rc --trailing-comma --use-parentheses --line-width=88 --check-only .) && (black -t py39 --check .)

format:
	isort -rc --trailing-comma --use-parentheses --line-width=88 .
	black -t py39 .

pylint: format-check
	pylint src/* tests/*

pyright: pylint
	pyright

test:
	python -m pytest tests
