package httpserver

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

func (s *Server) handleStream(c *gin.Context) {
	projectID := c.Param("projectID")
	ch := s.sseBroker.Subscribe(projectID)
	defer s.sseBroker.Unsubscribe(projectID, ch)

	c.Writer.Header().Set("Content-Type", "text/event-stream")
	c.Writer.Header().Set("Cache-Control", "no-cache")
	c.Writer.Header().Set("Connection", "keep-alive")

	c.Stream(func(w io.Writer) bool {
		select {
		case msg := <-ch:
			c.SSEvent("message", msg)
			return true
		case <-c.Request.Context().Done():
			return false
		}
	})
}

type adminLoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (s *Server) handleAdminLogin(c *gin.Context) {
	var req adminLoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid payload"})
		return
	}

	adminID, hash, err := s.adminRepo.GetAdminHashByEmail(c.Request.Context(), req.Email)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credential"})
		return
	}
	if err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credential"})
		return
	}

	claims := jwt.MapClaims{
		"sub": adminID,
		"exp": time.Now().Add(2 * time.Hour).Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(s.cfg.AdminJWTKey))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot create token"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"token": signed, "expires_in": 7200})
}

type createUserRequest struct {
	Email     string `json:"email"`
	Password  string `json:"password"`
	ProjectID string `json:"project_id"`
}

func (s *Server) handleCreateUser(c *gin.Context) {
	var req createUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid payload"})
		return
	}
	hashed, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot hash password"})
		return
	}
	id, err := s.projectUserRepo.CreateProjectUser(c.Request.Context(), req.Email, string(hashed), req.ProjectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot create user"})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"id": id, "email": req.Email, "project_id": req.ProjectID})
}

func (s *Server) handleCreateAPIKey(c *gin.Context) {
	projectID := c.Param("projectId")
	accessKeyID := "ak_" + uuid.NewString()
	plainSecret := "sk_" + uuid.NewString()
	hash, err := bcrypt.GenerateFromPassword([]byte(plainSecret), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot hash secret"})
		return
	}

	if err := s.apiKeyRepo.CreateAccessKey(c.Request.Context(), projectID, accessKeyID, string(hash), "mvp key"); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot create access key"})
		return
	}
	c.JSON(http.StatusCreated, gin.H{
		"project_id":        projectID,
		"access_key_id":     accessKeyID,
		"access_key_secret": plainSecret,
	})
}

func (s *Server) handleIngest(c *gin.Context) {
	projectID, _ := c.Get("project_id")
	fileHeader, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "missing file"})
		return
	}

	src, err := fileHeader.Open()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid file"})
		return
	}
	defer src.Close()
	content, err := io.ReadAll(src)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "cannot read file"})
		return
	}

	documentID := uuid.NewString()
	if _, err := s.db.ExecContext(
		c.Request.Context(),
		`INSERT INTO documents(id, project_id, file_name, status, vector_count)
		 VALUES($1::uuid, $2::uuid, $3, 'processing', 0)`,
		documentID, projectID.(string), fileHeader.Filename,
	); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot store document"})
		return
	}

	result, err := s.callAIIngest(c.Request.Context(), projectID.(string), documentID, fileHeader.Filename, content)
	if err != nil {
		_, _ = s.db.ExecContext(
			c.Request.Context(),
			`UPDATE documents SET status = 'failed' WHERE id = $1::uuid`,
			documentID,
		)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "ingest failed"})
		return
	}

	status := "ready"
	if _, err := s.db.ExecContext(
		c.Request.Context(),
		`UPDATE documents SET status = $1, vector_count = $2 WHERE id = $3::uuid`,
		status, result.Chunks, documentID,
	); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "cannot update document"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"document_id": documentID,
		"status":      status,
		"chunks":      result.Chunks,
	})
}

func (s *Server) handleQuery(c *gin.Context) {
	projectID, _ := c.Get("project_id")
	var payload struct {
		Query  string `json:"query"`
		UsePro bool   `json:"use_pro"`
	}
	if err := c.ShouldBindJSON(&payload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid payload"})
		return
	}

	resp, err := s.callAIQuery(c.Request.Context(), projectID.(string), payload.Query, payload.UsePro)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "query failed"})
		return
	}
	c.JSON(http.StatusOK, resp)
}

type ingestResult struct {
	ProjectID string `json:"project_id"`
	Chunks    int    `json:"chunks"`
	Status    string `json:"status"`
}

func (s *Server) callAIIngest(
	ctx context.Context,
	projectID, documentID, fileName string,
	content []byte,
) (*ingestResult, error) {
	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	_ = writer.WriteField("project_id", projectID)
	_ = writer.WriteField("document_id", documentID)
	part, err := writer.CreateFormFile("file", fileName)
	if err != nil {
		return nil, err
	}
	if _, err := part.Write(content); err != nil {
		return nil, err
	}
	_ = writer.Close()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, s.cfg.AIEngineURL+"/ingest", &body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	httpClient := &http.Client{Timeout: 30 * time.Second}
	res, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode >= 300 {
		return nil, fmt.Errorf("ai ingest status: %d", res.StatusCode)
	}
	var out ingestResult
	if err := json.NewDecoder(res.Body).Decode(&out); err != nil {
		return nil, err
	}
	return &out, nil
}

func (s *Server) callAIQuery(ctx context.Context, projectID, query string, usePro bool) (gin.H, error) {
	payload := map[string]any{
		"project_id": projectID,
		"query":      query,
		"use_pro":    usePro,
	}
	raw, _ := json.Marshal(payload)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, s.cfg.AIEngineURL+"/query", bytes.NewReader(raw))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	httpClient := &http.Client{Timeout: 30 * time.Second}
	res, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	if res.StatusCode >= 300 {
		return nil, fmt.Errorf("ai query status: %d", res.StatusCode)
	}
	var out map[string]any
	if err := json.NewDecoder(res.Body).Decode(&out); err != nil {
		return nil, err
	}
	return out, nil
}
