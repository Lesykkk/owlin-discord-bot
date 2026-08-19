VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYRIGHT := $(VENV)/bin/pyright

.PHONY: install check run

install:
	test -x $(PYTHON) || python3.13 -m venv $(VENV)
	$(PIP) install -r requirements.txt

check:
	$(PYTHON) -m ruff check
	$(PYTHON) -m ruff format --check
	$(PYRIGHT)
	$(PYTHON) -m mypy
	PYTHONPATH=src $(PYTHON) -m pylint src/owlin_bot
	PYTHONPATH=src $(PYTHON) -m pytest -q --cov=owlin_bot --cov-report=term-missing

run:
	PYTHONPATH=src $(PYTHON) -m owlin_bot.main
