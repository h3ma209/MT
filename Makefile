.PHONY: help build up down restart logs shell test clean dev

.DEFAULT_GOAL := help

# Colors
BLUE := \033[36m
GREEN := \033[32m
NC := \033[0m

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build docker image
	@echo "$(GREEN)Building MT service...$(NC)"
	docker-compose build

up: ## Start MT service
	@echo "$(GREEN)Starting MT service...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)MT API available at http://localhost:9322$(NC)"

down: ## Stop MT service
	@echo "$(BLUE)Stopping MT service...$(NC)"
	docker-compose down

restart: ## Restart MT service
	@echo "$(BLUE)Restarting MT service...$(NC)"
	docker-compose restart

logs: ## View logs
	docker-compose logs -f

shell: ## Open shell in MT container
	docker-compose exec drift-mt /bin/bash

test: ## Test MT API endpoints
	@echo "$(BLUE)Testing Health...$(NC)"
	@curl -s http://localhost:9322/docs || echo "Service not running"
	@echo "\n$(BLUE)Testing Translation (EN->AR)...$(NC)"
	@curl -s -X POST http://localhost:9322/translate \
		-H 'Content-Type: application/json' \
		-d '{"text": "Hello, how are you?", "source_lang": "en", "target_lang": "ar"}' | python3 -m json.tool
	@echo "\n$(BLUE)Testing Translation All Languages...$(NC)"
	@curl -s -X POST http://localhost:9322/translate/all \
		-H 'Content-Type: application/json' \
		-d '{"text": "Hello, how are you?", "source_lang": "en"}' | python3 -m json.tool

dev: ## Run locally without Docker
	@echo "$(GREEN)Starting MT server locally...$(NC)"
	python3 server.py

clean: ## Remove containers and images
	@read -p "Are you sure? This will delete containers and images! [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker rmi drift-mt 2>/dev/null || true; \
		docker system prune -f; \
	fi

setup: build up ## Full setup (build and start)
	@echo "$(GREEN)MT service is ready!$(NC)"
