# AGENTS Context Guide

Tài liệu này giúp AI agent hiểu nhanh quy tắc cốt lõi của repo.

## Non-negotiable Invariants
- Tenant isolation là bắt buộc: luôn áp `project_id` ở API, service, repository, vector filter.
- Không hard-code tenant dữ liệu thật trong code sản phẩm.
- Mọi request đi qua Gateway phải có auth context hợp lệ.

## Service Boundaries
- `services/gateway`: external API, auth, quota/rate-limit, SSE.
- `services/ai-engine`: parsing/chunking/embedding/retrieval/generation.
- `shared/proto`: source of truth cho contracts liên service.
- `infra`: chỉ chứa tài nguyên môi trường, không chứa business logic.

## Error and Status Mapping
- Gateway trả chuẩn RESTful status code.
- Lỗi từ AI Engine/gRPC phải map thành lỗi có ngữ nghĩa cho client.
- Ưu tiên error wrapping để giữ root cause.

## Definition of Done
- Có test hoặc smoke test cho thay đổi chính.
- Không phá backward compatibility contracts nếu chưa bump version.
- Docs cập nhật nếu behavior thay đổi.

## Agent Workflow
1. Đọc `ARCHITECTURE.md` trước khi sửa flow.
2. Kiểm tra `shared/proto` trước khi đổi giao tiếp Go/Python.
3. Chạy lệnh lint/test tối thiểu trước khi hoàn tất.
