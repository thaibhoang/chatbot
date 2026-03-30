#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
PROJECT_ID="${PROJECT_ID:-00000000-0000-0000-0000-000000000001}"
SAMPLE_FILE="${SAMPLE_FILE:-/tmp/mvp_doc.txt}"

echo "Preparing sample document..."
echo "RAG MVP sample content about project onboarding." > "$SAMPLE_FILE"

echo "Admin login..."
LOGIN_JSON=$(curl -sS -X POST "$BASE_URL/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")
TOKEN=$(printf '%s' "$LOGIN_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

echo "Create project user..."
curl -sS -X POST "$BASE_URL/v1/admin/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user1@local\",\"password\":\"user123\",\"project_id\":\"$PROJECT_ID\"}" >/dev/null

echo "Create access key..."
KEY_JSON=$(curl -sS -X POST "$BASE_URL/v1/admin/projects/$PROJECT_ID/api-keys" \
  -H "Authorization: Bearer $TOKEN")
ACCESS_KEY_ID=$(printf '%s' "$KEY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_key_id"])')
ACCESS_KEY_SECRET=$(printf '%s' "$KEY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_key_secret"])')

echo "Ingest document..."
curl -sS -X POST "$BASE_URL/v1/documents:ingest" \
  -H "X-Access-Key-Id: $ACCESS_KEY_ID" \
  -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" \
  -F "file=@$SAMPLE_FILE"

echo
echo "Query RAG..."
curl -sS -X POST "$BASE_URL/v1/query" \
  -H "X-Access-Key-Id: $ACCESS_KEY_ID" \
  -H "X-Access-Key-Secret: $ACCESS_KEY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?","use_pro":false}'
echo
echo "Smoke flow completed."
