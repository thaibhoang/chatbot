# Test Plan MVP

## Auth
- [ ] Login dung/sai credential.
- [ ] Access key dung/sai.

## Tenant Isolation
- [ ] Project A khong query du lieu cua Project B.

## Ingest
- [ ] Upload txt.
- [ ] Upload pdf.
- [ ] Upload docx.
- [ ] Document status dung (`processing/ready/failed`).

## Query
- [ ] Query tra answer co context retrieval.
- [ ] Query stream tra event `token` va ket thuc bang `done`.

## Smoke E2E
- [ ] login -> create user -> create key -> ingest -> query.

## Evidence
- 2026-03-30:
  - Gateway: `cd services/gateway && go mod tidy && go test ./...` (pass).
  - AI Engine syntax: `cd services/ai-engine && python3 -m compileall app` (pass).
  - AI Engine test: `cd services/ai-engine && PYTHONPATH=. .venv/bin/pytest -q` (pass, 1 test).
  - Smoke script da them: `scripts/smoke_mvp.sh` (chay sau khi `docker compose up --build` va co OpenAI key hop le).
  - Non-stream query: `POST /v1/query` tra JSON answer (pass).
  - Stream query: `POST /v1/query:stream` tra SSE event `token`...`done` (pass).
