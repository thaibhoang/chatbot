package middleware

import (
	"context"
	"net/http"

	"github.com/gin-gonic/gin"
)

type accessKeyRepo interface {
	VerifyAccessKey(ctx context.Context, accessKeyID, secret string) (string, error)
}

func AccessKeyAuth(repo accessKeyRepo) gin.HandlerFunc {
	return func(c *gin.Context) {
		accessKeyID := c.GetHeader("X-Access-Key-Id")
		accessKeySecret := c.GetHeader("X-Access-Key-Secret")
		if accessKeyID == "" || accessKeySecret == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing access key"})
			return
		}

		projectID, err := repo.VerifyAccessKey(c.Request.Context(), accessKeyID, accessKeySecret)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid access key"})
			return
		}

		c.Set("project_id", projectID)
		c.Next()
	}
}
