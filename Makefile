SHELL := /bin/bash

.PHONY: up down logs fmt lint test test-gateway test-ai proto

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

fmt:
	cd services/gateway && gofmt -w $$(rg --files -g '*.go')
	cd services/ai-engine && python -m compileall app

lint:
	cd services/gateway && go vet ./...
	cd services/ai-engine && python -m compileall app

test: test-gateway test-ai

test-gateway:
	cd services/gateway && go test ./...

test-ai:
	cd services/ai-engine && python -m pytest -q tests

proto:
	@echo "TODO: add protoc generation command for Go/Python stubs"
