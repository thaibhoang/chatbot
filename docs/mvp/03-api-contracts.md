# API Contracts (MVP)

## Admin APIs
- `POST /v1/admin/login`
  - Request: `{ "email": "...", "password": "..." }`
  - Response: `{ "token": "...", "expires_in": 3600 }`
- `POST /v1/admin/users` (JWT)
  - Request: `{ "email": "...", "password": "...", "project_id": "uuid" }`
  - Response: `{ "id": "uuid", "email": "...", "project_id": "uuid" }`
- `POST /v1/admin/projects/:projectId/api-keys` (JWT)
  - Response: `{ "access_key_id": "...", "access_key_secret": "...", "project_id": "uuid" }`

## User APIs
- `POST /v1/documents:ingest` (Access Key headers)
  - multipart: `file`
  - Response: `{ "document_id": "uuid", "status": "processing|ready|failed", "chunks": 0 }`
- `POST /v1/query` (Access Key headers)
  - Request: `{ "query": "...", "use_pro": false, "provider": "openai|gemini|claude" }`
  - `provider` la optional; neu bo qua se fallback ve provider cau hinh tren AI Engine.
  - Response: `{ "project_id": "uuid", "answer": "..." }`
- `POST /v1/query:stream` (Access Key headers, SSE)
  - Request: `{ "query": "...", "use_pro": false, "provider": "openai|gemini|claude" }`
  - Response stream events:
    - `event: token` with chunk payload
    - `event: done` when completed
    - `event: error` on failures

## Error Mapping
- `401`: missing/invalid JWT or access key.
- `403`: khong du quyen thao tac project.
- `404`: project/document khong ton tai.
- `422`: payload khong hop le.
- `429`: rate-limit exceeded.
- `500`: loi noi bo da wrap root cause.
