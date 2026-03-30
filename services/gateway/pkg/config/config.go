package config

import (
	"os"
	"strconv"
)

type Config struct {
	HTTPAddr               string
	GRPCTarget             string
	AIEngineURL            string
	RateLimitRPS           int
	PostgresDSN            string
	AdminJWTKey            string
	APIKeyEncryptionSecret string
	BootstrapAdminEmail    string
	BootstrapAdminPassword string
}

func Load() Config {
	return Config{
		HTTPAddr:     getenv("GATEWAY_HTTP_ADDR", ":8080"),
		GRPCTarget:   getenv("GATEWAY_GRPC_TARGET", "ai-engine:50051"),
		AIEngineURL:  getenv("AI_ENGINE_URL", "http://ai-engine:8000/v1"),
		RateLimitRPS: getenvInt("GATEWAY_RATE_LIMIT_RPS", 20),
		PostgresDSN: getenv(
			"GATEWAY_POSTGRES_DSN",
			"postgres://omnirag:omnirag@postgres:5432/omnirag?sslmode=disable",
		),
		AdminJWTKey:            getenv("GATEWAY_ADMIN_JWT_KEY", "change-me"),
		APIKeyEncryptionSecret: getenv("GATEWAY_API_KEY_ENCRYPTION_SECRET", "replace-me-32bytes-secret-key----"),
		BootstrapAdminEmail:    getenv("GATEWAY_BOOTSTRAP_ADMIN_EMAIL", "admin@local"),
		BootstrapAdminPassword: getenv("GATEWAY_BOOTSTRAP_ADMIN_PASSWORD", "admin123"),
	}
}

func getenv(k, def string) string {
	v := os.Getenv(k)
	if v == "" {
		return def
	}
	return v
}

func getenvInt(k string, def int) int {
	v := os.Getenv(k)
	n, err := strconv.Atoi(v)
	if err != nil {
		return def
	}
	return n
}
