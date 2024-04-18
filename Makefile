APP_NAME=songbirdcli
REQUIREMENTS_FILE=requirements.txt

.PHONY: env
env:
# check ENV env var has been set
ifndef ENV
	$(error Must set ENV variable!)
endif
# load env vars from .env file if present
ifneq ("$(wildcard $(ENV).env)", "")
	@echo "Loading configuration from $(ENV).env"
# include cannot be indented
include $(ENV).env
else
	@echo "Continuing without .env file."
	@echo "Creating template $(ENV).env file"
	echo 'RUN_LOCAL=false' > $(ENV).env
	echo 'ITUNES_ENABLED=true' >> $(ENV).env
	echo 'GDRIVE_ENABLED=true' >> $(ENV).env
endif

# variables as a list, required for pytest targets
# in this makefile
ENV_VARS = $(shell cat $(ENV).env | xargs)

.PHONY: setup
setup:
	@echo sets up the development environment
	python3 -m venv venv
	@echo activate venv with 'source venv/bin/activate'

# /app/data folder is legacy for backwards compatability
# from the times before songbird was split across
# core, cli and api.
.PHONY: volumesinit
volumesinit:
	mkdir -p ./$(APP_NAME)/data/dump
	mkdir -p ./$(APP_NAME)/data/local_chromium
	mkdir -p ./$(APP_NAME)/data/gdrive

.PHONY: volumesclean
volumesclean:
	rm -rf ./$(APP_NAME)/data/dump
	rm -rf ./$(APP_NAME)/data/local_chromium
	rm -rf ./$(APP_NAME)/data/gdrive

.PHONY: requirements
requirements: env
	pip install -r $(APP_NAME)/$(REQUIREMENTS_FILE)
# only install dependencies locally if in dev env
ifeq ($(ENV), dev)
	echo "install dev dependencies"
	pip install -e .[dev]
	pip install -e ../songbirdcore
else
	pip install -e .
endif
	playwright install

.PHONY: update-requirements
update-requirements: env
	pip uninstall songbirdcore
	pip freeze --exclude-editable | xargs pip uninstall -y
	rm $(APP_NAME)/$(REQUIREMENTS_FILE) || true
	pip install -r $(APP_NAME)/requirements.txt.blank
	pip freeze --exclude-editable > $(APP_NAME)/$(REQUIREMENTS_FILE)

# documentation targets
.PHONY: docs-lint
docs-lint:
	@echo linting files at docs/**/*.md
	markdownlint docs/**/*.md

.PHONY: docs-serve
docs-serve:
	@echo serving the site on http://localhost:8000
	mkdocs serve

.PHONY: docs-build
docs-build:
	@echo building the site
	mkdocs build --strict --verbose --site-dir public

.PHONY: build
build:
	docker build -t $(APP_NAME):latest .

.PHONY: run-itunes
run-itunes:
	docker run -it --env-file docker.env \
        -v "${HOME}"/songbirdcli/data/dump:/app/data/dump \
        -v "${HOME}"/songbirdcli/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
        -v "${HOME}"/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ Music.localized:/app/data/itunesauto \
        -v "${HOME}"/Music/Itunes/Itunes\ Media/Music:/app/data/ituneslib \
		$(APP_NAME):latest

.PHONY: run-gdrive
run-gdrive:
	docker run -it --env-file docker.env \
		-v "${PWD}"/songbirdcli/data/dump:/app/data/dump \
		-v "${PWD}"/songbirdcli/data/local_chromium:/root/.local/share/pyppeteer/local-chromium \
		-v "${PWD}"/songbirdcli/data/gdrive:/app/data/gdrive \
		-p 8080:8080 \
		--hostname songbird \
		$(APP_NAME):latest

.PHONY: run-default
run-default:
	docker run -it --env-file docker.env \
		-v "${PWD}"/songbirdcli/data/dump:/app/data/dump \
		$(APP_NAME):latest 

.PHONY: clean
clean:
	docker rm $(APP_NAME) || true

.PHONY: stop
stop:
	docker kill $(APP_NAME)

.PHONY: dev
dev: clean build run

lint:
	black $(APP_NAME)/.
	black tests

.PHONY: test-cov
test-stdout:
	python -m pytest --cov=songbirdcli tests/unit -v

.PHONY: test
test:
	python -m pytest --doctest-modules --junitxml=junit/test-results.xml --cov=songbirdcli --cov-report=xml --cov-report=html tests/unit -v

.PHONY: test-env
test-env:
	$(ENV_VARS) python -m pytest --doctest-modules --junitxml=junit/test-results.xml --cov=songbirdcli --cov-report=xml --cov-report=html tests/unit -v