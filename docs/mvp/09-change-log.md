# Change Log MVP

## 2026-03-30
- Khoi tao bo tai lieu `docs/mvp/*`.
- Chuan hoa scope MVP OpenAI-first, API-only.
- Dinh nghia phase/task/test/risk cho Agent thuc thi.
- Them migration `002_auth_users.sql` cho `admin_users`, `project_users`.
- Gateway: them admin JWT auth, endpoint admin login/create user/create access key.
- Gateway: thay access key auth stub bang verify hash secret tu Postgres.
- Gateway: them endpoint `POST /v1/documents:ingest`, `POST /v1/query`, access log middleware.
- AI Engine: them OpenAI client, embedding + generation, parse txt/pdf/docx, upsert/search Qdrant theo `project_id`.
- Cap nhat `.env.example` voi bien OpenAI/Gateway auth; `docker-compose.yml` su dung `.env`.
- Them smoke script `scripts/smoke_mvp.sh`.
