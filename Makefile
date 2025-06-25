
ar:
	@if [ -z "$(m)" ]; then \
		read -p "Enter migration message: " m; \
	else \
		m="$(m)"; \
	fi; \
	alembic revision --autogenerate -m "$$m"

auh:
	alembic upgrade head

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app

up:
	docker compose up --build

down:
	docker compose down

clear:
	docker system prune

test:
	pytest tests


SERVER_IP := 192.168.104.131
DOCKER_REGISTRY := $(SERVER_IP):5000
PROJECT_NAME := docsbox-backend

manual-deploy:
	docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest .
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest
	ssh -v egorzh@$(SERVER_IP) "docker pull $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest || { echo 'Failed to pull $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest'; exit 1; }"
	ssh -v egorzh@$(SERVER_IP) "cd /home/egorzh/docsbox-server && docker compose up -d $(PROJECT_NAME) || { echo 'Failed to start containers'; exit 1; }"
