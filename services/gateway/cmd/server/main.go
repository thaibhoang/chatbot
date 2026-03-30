package main

import (
	"log"

	"github.com/thaibhoang/chatbot/services/gateway/internal/httpserver"
	"github.com/thaibhoang/chatbot/services/gateway/pkg/config"
)

func main() {
	cfg := config.Load()
	srv := httpserver.New(cfg)

	if err := srv.Run(); err != nil {
		log.Fatalf("gateway stopped: %v", err)
	}
}
