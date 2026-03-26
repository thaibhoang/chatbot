# Quality Gates

## Bắt buộc trước khi merge
- Gateway: `go test ./...` và `go vet ./...` pass.
- AI Engine: `pytest -q tests` pass.
- Không có thay đổi contract breaking trong `shared/proto` nếu chưa bump version.
- Xác nhận tenant isolation: mọi truy vấn vector có filter `project_id`.

## Recommended Checks
- Smoke test stream từ AI Engine sang Gateway SSE.
- Kiểm tra auth key flow với dữ liệu Postgres mẫu.
- Đảm bảo docs cập nhật khi đổi endpoint hoặc sequence flow.
