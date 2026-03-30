# Risk Log

## R1 - Sai tenant filter
- Impact: ro ri du lieu giua projects.
- Mitigation: bat buoc filter `project_id` + test negative.

## R2 - Chi phi OpenAI
- Impact: vuot ngan sach.
- Mitigation: gioi han do dai context, rate-limit, quota co ban.

## R3 - Loi parser tai lieu
- Impact: ingest that bai.
- Mitigation: fallback parser, trang thai failed ro ly do.

## R4 - Secret leakage
- Impact: mat an toan.
- Mitigation: hash secret, khong log key, rotate key.
