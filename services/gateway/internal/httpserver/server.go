package httpserver

import (
	"net/http"

	"github.com/amcolab/omni-rag/services/gateway/internal/httpserver/middleware"
	"github.com/amcolab/omni-rag/services/gateway/internal/stream"
	"github.com/amcolab/omni-rag/services/gateway/pkg/config"
	"github.com/gin-gonic/gin"
)

type Server struct {
	cfg       config.Config
	router    *gin.Engine
	sseBroker *stream.Broker
}

func New(cfg config.Config) *Server {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.RequestID())
	r.Use(middleware.RateLimit(cfg.RateLimitRPS))

	s := &Server{
		cfg:       cfg,
		router:    r,
		sseBroker: stream.NewBroker(),
	}
	s.routes()
	return s
}

func (s *Server) Run() error {
	return s.router.Run(s.cfg.HTTPAddr)
}

func (s *Server) routes() {
	s.router.GET("/healthz", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})
	v1 := s.router.Group("/v1")
	v1.Use(middleware.AccessKeyAuth())
	v1.GET("/stream/:projectID", s.handleStream)
}
