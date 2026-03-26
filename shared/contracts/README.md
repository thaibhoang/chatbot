# Shared Contracts

## Versioning Rules
- Thay đổi backward-compatible: thêm field mới với số thứ tự mới trong proto.
- Không tái sử dụng field number đã xóa.
- Breaking change phải bump version package (`v1` -> `v2`).

## Ownership
- Team Gateway và AI Engine đồng sở hữu thư mục này.
- Mọi thay đổi contract bắt buộc có test tích hợp cho cả 2 service.
