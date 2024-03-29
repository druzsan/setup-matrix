SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.PHONY: help
help: ## Print this help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: init
init:  # Install all dependencies
	pip install -IUr requirements.txt -r requirements-dev.txt

.PHONY: clean
clean: ## Clean project
	rm -rf .ruff_cache/ .mypy_cache/ node_modules/ .direnv/ .venv/

.PHONY: check-format
check-format: ## Check code formatting
	black --check .

.PHONY: format
format: ## Fix code formatting
	black .

.PHONY: typecheck
typecheck: ## Check code types
	mypy main.py
	mypy tests

.PHONY: lint
lint: ## Lint code
	ruff check main.py tests

.PHONY: test
test: ## Run unit-test
	python -m pytest

.PHONY: docker-image
docker-build:  # Build Docker image
	docker build -f Dockerfile -t setup-matrix .
