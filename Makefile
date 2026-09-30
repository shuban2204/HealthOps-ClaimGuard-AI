.PHONY: install-backend train test-backend install-frontend build-frontend dev-backend

install-backend:
	python -m pip install -r backend/requirements.txt

train:
	python ml/generate_data.py
	python ml/train.py

test-backend:
	$${PYTHON:-python} -m pytest backend/tests -q

install-frontend:
	cd frontend && npm install

build-frontend:
	cd frontend && npm run build

dev-backend:
	uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000

