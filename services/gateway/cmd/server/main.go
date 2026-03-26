package main

import (
	"log"

	"github.com/amcolab/omni-rag/services/gateway/internal/httpserver"
	"github.com/amcolab/omni-rag/services/gateway/pkg/config"
)

func main() {
	cfg := config.Load()
	srv := httpserver.New(cfg)

	if err := srv.Run(); err != nil {
		log.Fatalf("gateway stopped: %v", err)
	}
}
