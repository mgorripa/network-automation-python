.PHONY: venv deps generate diff backup deploy validate cleanup dry-run all

venv:
	python -m venv .venv

deps:
	pip install -r requirements.txt

generate:
	python scripts/deploy_async.py --generate-only

diff:
	python scripts/diff.py

backup:
	python scripts/backup.py

deploy:
	python scripts/deploy_async.py --max-workers 6

validate:
	python scripts/validate.py

cleanup:
	python scripts/cleanup.py

dry-run: generate diff

all: generate diff backup deploy validate
