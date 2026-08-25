# The "paved road": one command per task so the whole team stays consistent.
.PHONY: install lint test run build docker-run clean

install:
	pip install -r requirements.txt

lint:
	ruff check pipeline tests || true      # non-blocking demo; make it blocking in CI

test:
	pytest -q

run:
	python -m pipeline.transform

build:
	docker build -t sample-pipeline:local .

docker-run:
	docker run --rm sample-pipeline:local

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
