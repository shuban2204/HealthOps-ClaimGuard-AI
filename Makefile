PYTHON ?= python
NPM ?= npm
UVICORN ?= uvicorn
COMPOSE ?= docker compose

.PHONY: install-backend train test-backend install-frontend test-frontend build-frontend dev-backend dev-frontend test build docker-build docker-up docker-down smoke

install-backend:
	$(PYTHON) -m pip install -r backend/requirements.txt

train:
	$(PYTHON) ml/generate_data.py
	$(PYTHON) ml/train.py

test-backend:
	PYTHONPATH=backend $(PYTHON) -m pytest backend/tests -q

install-frontend:
	cd frontend && $(NPM) install

test-frontend:
	cd frontend && $(NPM) test

build-frontend:
	cd frontend && $(NPM) run build

dev-backend:
	PYTHONPATH=backend $(UVICORN) app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && $(NPM) run dev -- --host 127.0.0.1

test: test-backend test-frontend

build: build-frontend

docker-build:
	$(COMPOSE) build

docker-up:
	$(COMPOSE) up

docker-down:
	$(COMPOSE) down

smoke:
	$(PYTHON) -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=10).read().decode())"
