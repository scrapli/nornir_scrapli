lint:
	python -m isort .
	python -m black .
	python -m pylint nornir_scrapli/
	python -m pydocstyle .
	python -m mypy --strict nornir_scrapli/

darglint:
	find nornir_scrapli -type f \( -iname "*.py"\ ) | xargs darglint -x

test:
	python -m pytest \
	tests/

cov:
	python -m pytest \
	--cov=nornir_scrapli \
	--cov-report html \
	--cov-report term \
	tests/

test_unit:
	python -m pytest \
	tests/unit/

cov_unit:
	python -m pytest \
	--cov=nornir_scrapli \
	--cov-report html \
	--cov-report term \
	tests/unit/

.PHONY: docs
docs:
	python docs/generate.py

test_docs:
	mkdocs build --clean --strict
	htmltest -c docs/htmltest.yml -s
	rm -rf tmp

deploy_docs:
	mkdocs gh-deploy
