# Product Scope MVP

## Muc tieu
- API-only RAG chatbot da tenant.
- Admin login bang email/password + JWT.
- Admin tao user va access key theo project.
- User ingest tai lieu vao vector DB.
- User query va nhan cau tra loi RAG qua OpenAI.

## Non-goals
- Chua lam web UI.
- Chua lam thanh toan, billing, hay workflow phuc tap.

## Roles
- `admin`: quan tri users, projects, access keys.
- `user`: upload tai lieu va query voi access key.

## Success Criteria
- Hoan tat flow E2E: login -> tao user -> tao key -> ingest -> query.
- Tenant isolation dung o moi lop (API, service, vector filter).
