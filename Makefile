lint:
	python -m isort .
	python -m black .
	python -m pylama .
	python -m pydocstyle .
	python -m mypy nornir_scrapli/

cov:
	python -m pytest \
	--cov=nornir_scrapli \
	--cov-report html \
	--cov-report term \
	tests/

test:
	python -m pytest tests/

.PHONY: docs
docs:
	python docs/generate/generate_docs.py

deploy_docs:
	mkdocs gh-deploy
