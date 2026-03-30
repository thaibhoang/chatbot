package httpserver

import (
	"context"
	"database/sql"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
	"github.com/thaibhoang/chatbot/services/gateway/internal/httpserver/middleware"
	"github.com/thaibhoang/chatbot/services/gateway/internal/repository/postgres"
	"github.com/thaibhoang/chatbot/services/gateway/internal/stream"
	"github.com/thaibhoang/chatbot/services/gateway/pkg/config"
	"github.com/thaibhoang/chatbot/services/gateway/pkg/crypto"
	"golang.org/x/crypto/bcrypt"
)

type Server struct {
	cfg             config.Config
	router          *gin.Engine
	sseBroker       *stream.Broker
	db              *sql.DB
	apiKeyRepo      *postgres.APIKeyRepository
	projectAIConfig *postgres.ProjectAIConfigRepository
	secretCipher    *crypto.AESGCM
	adminRepo       *postgres.AdminRepository
	projectUserRepo *postgres.ProjectUserRepository
}

func New(cfg config.Config) *Server {
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.RequestID())
	r.Use(middleware.RateLimit(cfg.RateLimitRPS))
	r.Use(middleware.AccessLog())

	db, err := sql.Open("postgres", cfg.PostgresDSN)
	if err != nil {
		log.Fatalf("open postgres: %v", err)
	}

	secretCipher, err := crypto.NewAESGCM(cfg.APIKeyEncryptionSecret)
	if err != nil {
		log.Fatalf("create key cipher: %v", err)
	}

	s := &Server{
		cfg:             cfg,
		router:          r,
		sseBroker:       stream.NewBroker(),
		db:              db,
		apiKeyRepo:      postgres.NewAPIKeyRepository(db),
		projectAIConfig: postgres.NewProjectAIConfigRepository(db),
		secretCipher:    secretCipher,
		adminRepo:       postgres.NewAdminRepository(db),
		projectUserRepo: postgres.NewProjectUserRepository(db),
	}
	s.bootstrapAdmin()
	s.routes()
	return s
}

func (s *Server) Run() error {
	return s.router.Run(s.cfg.HTTPAddr)
}

func (s *Server) bootstrapAdmin() {
	ctx := context.Background()
	count, err := s.adminRepo.CountAdmins(ctx)
	if err != nil || count > 0 {
		return
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(s.cfg.BootstrapAdminPassword), bcrypt.DefaultCost)
	if err != nil {
		return
	}
	_, _ = s.adminRepo.CreateAdminUser(ctx, s.cfg.BootstrapAdminEmail, string(hash))
}

func (s *Server) routes() {
	s.router.GET("/healthz", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	admin := s.router.Group("/v1/admin")
	admin.POST("/login", s.handleAdminLogin)

	adminProtected := s.router.Group("/v1/admin")
	adminProtected.Use(middleware.AdminJWTAuth(s.cfg.AdminJWTKey))
	adminProtected.POST("/users", s.handleCreateUser)
	adminProtected.POST("/projects/:projectId/api-keys", s.handleCreateAPIKey)
	adminProtected.PUT("/projects/:projectId/ai-config", s.handleUpsertProjectAIConfig)
	adminProtected.GET("/projects/:projectId/ai-config", s.handleGetProjectAIConfig)

	user := s.router.Group("/v1")
	user.Use(middleware.AccessKeyAuth(s.apiKeyRepo))
	user.GET("/stream/:projectID", s.handleStream)
	user.POST("/documents:ingest", s.handleIngest)
	user.POST("/query", s.handleQuery)
	user.POST("/query:stream", s.handleQueryStream)
}
