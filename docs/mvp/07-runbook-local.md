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
8. Dat `GATEWAY_API_KEY_ENCRYPTION_SECRET` (chuoi bi mat, dai it nhat 32 ky tu).

## Run
1. `docker compose up --build`
2. Health check:
   - Gateway: `GET /healthz`
   - AI Engine: `GET /api/v1/health`

## Smoke
1. Admin login.
2. Tao user + API key.
3. Cau hinh AI theo project (admin JWT):
   - `curl -X PUT http://localhost:8080/v1/admin/projects/<projectId>/ai-config -H "Authorization: Bearer <admin_jwt>" -H "Content-Type: application/json" -d '{"provider":"claude","model":"claude-3-5-sonnet-latest","api_key":"<provider_key>"}'`
4. Ingest 1 tai lieu.
5. Query 1 cau hoi.
6. Test stream query:
   - `curl -N -X POST http://localhost:8080/v1/query:stream -H "X-Access-Key-Id: <id>" -H "X-Access-Key-Secret: <secret>" -H "Content-Type: application/json" -d '{"query":"...","use_pro":false,"provider":"gemini"}'`
7. Test query non-stream voi provider:
   - `curl -X POST http://localhost:8080/v1/query -H "X-Access-Key-Id: <id>" -H "X-Access-Key-Secret: <secret>" -H "Content-Type: application/json" -d '{"query":"...","use_pro":false,"provider":"claude"}'`
8. Hoac chay nhanh:
   - `./scripts/smoke_mvp.sh`

## Curl Cookbook (copy/paste)
1. Khai bao bien:
   - `BASE_URL=http://localhost:8080`
   - `ADMIN_EMAIL=admin@local`
   - `ADMIN_PASSWORD=admin123`
   - `PROJECT_ID=<project_uuid_da_ton_tai>`
   - `DOC_PATH=./sample.txt`

2. Health check:
   - `curl -s "$BASE_URL/healthz"`
   - `curl -s http://localhost:8000/api/v1/health`

3. Admin login lay JWT:
   - `ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/v1/admin/login" -H "Content-Type: application/json" -d '{"email":"'"$ADMIN_EMAIL"'","password":"'"$ADMIN_PASSWORD"'"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')`
   - `echo "$ADMIN_TOKEN"`

4. Tao project user:
   - `curl -s -X POST "$BASE_URL/v1/admin/users" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"email":"user1@local","password":"user123","project_id":"'"$PROJECT_ID"'"}'`

5. Tao access key:
   - `KEY_JSON=$(curl -s -X POST "$BASE_URL/v1/admin/projects/$PROJECT_ID/api-keys" -H "Authorization: Bearer $ADMIN_TOKEN")`
   - `ACCESS_KEY_ID=$(echo "$KEY_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_key_id"])')`
   - `ACCESS_KEY_SECRET=$(echo "$KEY_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_key_secret"])')`
   - `echo "$ACCESS_KEY_ID"`
   - `echo "$ACCESS_KEY_SECRET"`

6. Upsert cau hinh AI theo project (vi du Claude):
   - `curl -s -X PUT "$BASE_URL/v1/admin/projects/$PROJECT_ID/ai-config" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d '{"provider":"claude","model":"claude-3-5-sonnet-latest","api_key":"<provider_key>"}'`

7. Lay cau hinh AI hien tai:
   - `curl -s -X GET "$BASE_URL/v1/admin/projects/$PROJECT_ID/ai-config" -H "Authorization: Bearer $ADMIN_TOKEN"`

8. Ingest tai lieu:
   - `curl -s -X POST "$BASE_URL/v1/documents:ingest" -H "X-Access-Key-Id: $ACCESS_KEY_ID" -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" -F "file=@$DOC_PATH"`

9. Query non-stream (provider fallback theo project config):
   - `curl -s -X POST "$BASE_URL/v1/query" -H "X-Access-Key-Id: $ACCESS_KEY_ID" -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" -H "Content-Type: application/json" -d '{"query":"Tom tat tai lieu vua ingest","use_pro":false}'`

10. Query non-stream voi provider override:
   - `curl -s -X POST "$BASE_URL/v1/query" -H "X-Access-Key-Id: $ACCESS_KEY_ID" -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" -H "Content-Type: application/json" -d '{"query":"Tra loi ngan gon","use_pro":false,"provider":"gemini"}'`

11. Query stream SSE:
   - `curl -N -X POST "$BASE_URL/v1/query:stream" -H "X-Access-Key-Id: $ACCESS_KEY_ID" -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" -H "Content-Type: application/json" -d '{"query":"Tra loi dang stream","use_pro":false}'`
