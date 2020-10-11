lint:
	python -m isort nornir_scrapli/
	python -m isort examples/
	python -m isort tests/
	python -m black nornir_scrapli/
	python -m black examples/
	python -m black tests/
	python -m pylama nornir_scrapli/
	python -m pydocstyle nornir_scrapli/
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
	rm -rf docs/nornir_scrapli
	python -m pdoc \
	--html \
	--output-dir docs \
	nornir_scrapli \
	--force
