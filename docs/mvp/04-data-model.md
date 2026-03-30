# Data Model MVP

## Core Tables
- `projects(id, name, status, created_at)`
- `api_keys(id, project_id, access_key_id, access_key_secret_hash, description, last_used)`
- `documents(id, project_id, file_name, status, vector_count, created_at)`

## New Tables
- `admin_users(id, email unique, password_hash, status, created_at, updated_at)`
- `project_users(id, email unique, password_hash, project_id, status, created_at, updated_at)`
- `project_ai_configs(id, project_id unique where active, provider, model, api_key_encrypted, status, created_at, updated_at)`

## Lifecycle
- API key: create -> active -> revoke(optional MVP+1).
- Project AI config: upsert active config theo project -> rotate key/model/provider bang upsert.
- Document: processing -> ready|failed.

## Tenant Isolation Rules
- Du lieu business gan `project_id`.
- Access key map den duy nhat 1 `project_id`.
- Qdrant payload bat buoc co `project_id`, `document_id`.
