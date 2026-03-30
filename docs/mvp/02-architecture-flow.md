# Architecture Flow MVP

## Components
- Gateway (Go): REST API, JWT admin auth, access key auth, rate limit.
- AI Engine (Python): ingest, retrieval, generation.
- Postgres: projects, users, api_keys, documents.
- Qdrant: vector store voi payload co `project_id`.
- OpenAI: generation provider mac dinh.

## Flow
1. Admin login tai Gateway va lay JWT.
2. Admin tao user / access key theo project.
3. User gui ingest/query kem `X-Access-Key-Id` + `X-Access-Key-Secret`.
4. Gateway verify key, resolve `project_id`, goi AI Engine.
5. AI Engine ingest/query voi filter tenant bat buoc.

## Invariants
- Khong hardcode tenant.
- Moi query vector phai filter `project_id`.
- Gateway phai xac thuc context truoc khi xu ly.
