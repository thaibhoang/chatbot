# Omni-RAG Shared Service

Omni-RAG là hệ thống sidecar/microservices gồm:
- Go Gateway: auth, rate-limit, quota, SSE cho client.
- Python AI Engine: ingest/query RAG, tích hợp Gemini, truy vấn Qdrant.
- PostgreSQL + Qdrant: lưu tenant config và vector embeddings.

## Cấu trúc chính
- `services/gateway`: API gateway bằng Go (Gin + gRPC client).
- `services/ai-engine`: AI engine bằng FastAPI async.
- `shared/proto`: hợp đồng gRPC dùng chung.
- `infra`: Dockerfiles, migrations, bootstrap scripts.

## Chạy local với Docker Compose
1. Copy biến môi trường:
   - `cp .env.example .env`
2. Khởi động stack:
   - `docker compose up --build`
3. Kiểm tra service:
   - Gateway health: `http://localhost:8080/healthz`
   - AI Engine health: `http://localhost:8000/v1/healthz`
   - AI docs: `http://localhost:8000/docs`

## Luồng dữ liệu
1. Client gọi Gateway với access key.
2. Gateway xác thực + áp quota/rate-limit.
3. Gateway gọi AI Engine qua gRPC/HTTP nội bộ.
4. AI Engine parse/chunk/embed và search Qdrant theo `project_id`.
5. AI Engine stream token về Gateway, Gateway phát SSE tới client.
