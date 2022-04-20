
.PHONY: format-check format pylint pyright test

format-check:
	black -t py39 --check .

format:
	black -t py39 .

pylint: format-check
	pylint

pyright: pylint
	pyright

test:
	python -m pytest tests
