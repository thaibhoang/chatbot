FROM golang:1.22 AS builder
WORKDIR /app

COPY services/gateway/go.mod services/gateway/go.sum* ./services/gateway/
WORKDIR /app/services/gateway
RUN go mod download || true

COPY services/gateway/ .
RUN go build -o /gateway ./cmd/server

FROM gcr.io/distroless/base-debian12
COPY --from=builder /gateway /gateway
EXPOSE 8080
ENTRYPOINT ["/gateway"]
