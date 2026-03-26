# Contributing

## Development Rules
- Go Gateway theo standard project layout, truyền `context.Context` xuyên suốt.
- Python AI Engine dùng FastAPI async, Pydantic cho toàn bộ request/response.
- Mọi thay đổi contracts trong `shared/proto` phải có kế hoạch tương thích ngược.

## Add New Service Checklist
1. Xác định boundary service và input/output contracts.
2. Thêm auth boundary: xác thực + tenant context propagation.
3. Thêm observability: logs, metrics, trace tối thiểu.
4. Viết test tối thiểu cho đường đi chính và lỗi phổ biến.
5. Cập nhật `ARCHITECTURE.md` nếu có thay đổi luồng.

## Pull Request Checklist
- [ ] Pass test cho service liên quan.
- [ ] Không vi phạm tenant isolation (`project_id` filter).
- [ ] Cập nhật docs khi thay đổi API/flow.
