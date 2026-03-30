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
- [ ] Query khong gui `provider` van fallback theo `AI_ENGINE_LLM_PROVIDER`.
- [ ] Query khong gui `provider` nhung co project ai-config thi dung provider/model tu DB.
- [ ] Query gui `provider=openai|gemini|claude` tra ket qua hop le (khi key hop le).
- [ ] Query gui `provider` khong hop le bi tu choi voi 4xx.
- [ ] Query stream voi `provider=gemini|claude` van co event `token` va `done`.

## Provider Scope
- [ ] Xac nhan embedding/retrieval van dung OpenAI cho moi provider generation.
- [ ] Xac nhan API key luu dang ma hoa trong DB, khong phai plaintext.

## Project AI Config API
- [ ] PUT `/v1/admin/projects/:projectId/ai-config` luu config hop le.
- [ ] GET `/v1/admin/projects/:projectId/ai-config` tra metadata, khong tra plaintext api_key.
- [ ] GET ai-config cho project chua cau hinh tra 404.

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
