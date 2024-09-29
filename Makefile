.PHONY: check-lint
check-lint:
	uv run ruff check src tests --quiet

.PHONY: check-format
check-format:
	uv run ruff format src tests --check --quiet

.PHONY: check-codestyle
check-codestyle: check-poetry check-lint check-format

.PHONY: codestyle
codestyle:
	uv run ruff check src tests --fix --unsafe-fixes
	uv run ruff format src tests

.PHONY: test
test:
	${MAKE} dev-up
	uv run pytest -vv tests

.PHONY: up-local
up-local: docker-cleanup
	docker compose --profile local up -d

build:
	docker compose build --no-cache imagestore

docker-cleanup:
	docker container kill $(shell docker container ls -qa) || true
	docker container rm $(shell docker container ls -qa) || true
	docker volume rm $(shell docker volume ls -q) || true
	docker network prune -f
	docker system prune -f

dev-up:
	docker compose up -d mongo minio
