package config

import (
	"os"
	"strconv"
)

type Config struct {
	HTTPAddr     string
	GRPCTarget   string
	RateLimitRPS int
}

func Load() Config {
	return Config{
		HTTPAddr:     getenv("GATEWAY_HTTP_ADDR", ":8080"),
		GRPCTarget:   getenv("GATEWAY_GRPC_TARGET", "ai-engine:50051"),
		RateLimitRPS: getenvInt("GATEWAY_RATE_LIMIT_RPS", 20),
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
