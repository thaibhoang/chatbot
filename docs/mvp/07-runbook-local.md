# Local Runbook

## Prerequisites
- Docker + Docker Compose
- Go toolchain
- Python 3.11+

## Env
1. Copy `.env.example` -> `.env`.
2. Dien `AI_ENGINE_OPENAI_API_KEY`.
3. Neu dung Gemini/Claude, dien them `AI_ENGINE_GEMINI_API_KEY` va `AI_ENGINE_CLAUDE_API_KEY`.
4. Co the dat provider mac dinh qua `AI_ENGINE_LLM_PROVIDER=openai|gemini|claude`.
5. Embedding hien tai van dung OpenAI, khong doi theo `provider` query.
6. Khong commit `.env`.
7. Dat `GATEWAY_ADMIN_JWT_KEY` khac gia tri mac dinh.

## Run
1. `docker compose up --build`
2. Health check:
   - Gateway: `GET /healthz`
   - AI Engine: `GET /api/v1/health`

## Smoke
1. Admin login.
2. Tao user + API key.
3. Ingest 1 tai lieu.
4. Query 1 cau hoi.
5. Test stream query:
   - `curl -N -X POST http://localhost:8080/v1/query:stream -H "X-Access-Key-Id: <id>" -H "X-Access-Key-Secret: <secret>" -H "Content-Type: application/json" -d '{"query":"...","use_pro":false,"provider":"gemini"}'`
6. Test query non-stream voi provider:
   - `curl -X POST http://localhost:8080/v1/query -H "X-Access-Key-Id: <id>" -H "X-Access-Key-Secret: <secret>" -H "Content-Type: application/json" -d '{"query":"...","use_pro":false,"provider":"claude"}'`
7. Hoac chay nhanh:
   - `./scripts/smoke_mvp.sh`
