APP_NAME=songbird

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
	"echo 'RUN_LOCAL=false' >> .env"
	"echo 'ITUNES_ENABLED=true' >> .env"
	"echo 'GDRIVE_ENABLED=true' >> .env"
endif

# variables as a list, required for pytest targets
# in this makefile
ENV_VARS = $(shell cat $(ENV).env | xargs)

.PHONY: setup
setup:
prefix: setup
	@echo sets up the development environment
	python3 -m venv venv
	@echo activate your venv with 'source venv/bin/activate'

.PHONY: volumesinit
volumesinit:
	mkdir -p app/data/dump
	mkdir -p app/data/local_chromium
	mkdir -p app/data/gdrive

.PHONY: volumesclean
volumesclean:
	rm -rf ./app/data/dump
	rm -rf ./app/data/local_chromium
	rm -rf ./app/data/gdrive

.PHONY: requirements
requirements:
	pip install black isort click
	pip install -r $(APP_NAME)/requirements.txt
	pip install -e .

.PHONY: build
build:
	docker build -t $(APP_NAME):latest .

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

test:
	$(ENV_VARS) python -m pytest test/unit -v