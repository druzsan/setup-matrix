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

.PHONY: docker-build
docker-build:  # Build Docker image
	docker build -f Dockerfile -t setup-matrix .

.PHONY: docker-run
docker-run:  # Run Docker image
docker-run: docker-build
	docker run -it --rm setup-matrix /bin/bash
