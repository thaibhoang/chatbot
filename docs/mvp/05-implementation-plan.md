# Implementation Plan (Agent Executable)

## Phase 0
- [x] Tao tai lieu MVP va checklist bat buoc.

## Phase 1 - Auth/Admin
- [x] DB migration cho `admin_users`, `project_users`.
- [x] `POST /v1/admin/login`.
- [x] `POST /v1/admin/users`.
- [x] `POST /v1/admin/projects/:projectId/api-keys`.
- [x] Verify access key that trong middleware + set `project_id`.

## Phase 2 - Ingest
- [x] Gateway endpoint `POST /v1/documents:ingest`.
- [x] AI Engine parse/chunk txt/pdf/docx.
- [x] Upsert vector voi payload tenant.
- [x] Cap nhat trang thai `documents`.

## Phase 3 - Query OpenAI
- [x] Gateway endpoint `POST /v1/query`.
- [x] Retrieval filter theo `project_id`.
- [x] Generation voi OpenAI provider.

## Phase 4 - Hardening
- [x] Error mapping nhat quan REST.
- [x] Logging co request_id, project_id, latency.
- [x] Cap nhat runbook local.

## Task Template
- Task-ID:
- Muc tieu:
- Files:
- Inputs:
- Outputs:
- Tests:
- Done when:
