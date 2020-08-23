necessary-packs:
	$(SUDO) pip3 install pipenv==2020.6.2

.PHONY: setup
setup: SUDO := sudo
setup: necessary-packs
setup:
	echo "Setup"
	pipenv run pipenv install --deploy --system

.PHONY: setup-dev
setup-dev: SUDO := sudo
setup-dev: necessary-packs
setup-dev:
	echo "Setup dev"
	pipenv run pipenv install --deploy --system --dev

.PHONY: autoflake
autoflake:
	pipenv run autoflake -r $(AUTOFLAKE_OPTIONS) --exclude */snapshots --remove-unused-variables --remove-all-unused-imports  **/ | tee autoflake.log
	echo "$(AUTOFLAKE_OPTIONS)" | grep -q -- '--in-place' || ! [ -s autoflake.log ]

.PHONY: isort
isort:
	pipenv run isort **/ --multi-line 3 --trailing-comma --line-width 88 --skip */snapshots $(ISORT_OPTIONS)

.PHONY: black
black:
	pipenv run black **/ --exclude '.*/snapshots' $(BLACK_OPTIONS)

.PHONY: lint
lint: ISORT_OPTIONS := --check-only
lint: BLACK_OPTIONS := --check
lint: autoflake isort black
	pipenv run mypy **/*.py --ignore-missing-imports
	pipenv run flake8 ./lmx --ignore=W291

.PHONY: format
format: AUTOFLAKE_OPTIONS := --in-place
format: autoflake isort black

.PHONY: dc
dc:
	docker-compose $(DOCKER_COMPOSE_OPTIONS)


.PHONY: up
up: DOCKER_COMPOSE_OPTIONS := up -d
up:	dc

.PHONY: build
build:
	$(SUDO) docker-compose -f docker-compose.yml up -d --build

.PHONY: sbuild
sbuild: SUDO := sudo
sbuild: build


.PHONY: down
down: DOCKER_COMPOSE_OPTIONS := down
down: dc

.PHONY: restart
restart: DOCKER_COMPOSE_OPTIONS := restart
restart: dc

