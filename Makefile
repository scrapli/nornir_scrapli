lint:
	python -m isort -rc -y .
	python -m black .
	python -m pylama .
	python -m pydocstyle .
	python -m mypy nornir_scrapli/
