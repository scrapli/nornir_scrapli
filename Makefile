NOX = uv run --locked --only-group nox nox

.PHONY: setup lint format darglint test cov test_unit cov_unit docs test_docs deploy_docs build

setup:
	uv sync --locked

lint:
	$(NOX) -s isort black pylint pydocstyle mypy

format:
	uv run --locked isort .
	uv run --locked black .

darglint:
	$(NOX) -s darglint

test test_unit:
	$(NOX) -s unit_tests-3.13

cov cov_unit:
	$(NOX) -s unit_tests-3.13 -- --cov-report=html

docs:
	uv run --locked --group docs python docs/generate.py

test_docs:
	$(NOX) -s docs
	htmltest -c docs/htmltest.yml -s
	rm -rf tmp

deploy_docs:
	uv run --locked --group docs mkdocs gh-deploy

build:
	$(NOX) -s build
