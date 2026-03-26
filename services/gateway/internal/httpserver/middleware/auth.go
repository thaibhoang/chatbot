package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func AccessKeyAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		accessKeyID := c.GetHeader("X-Access-Key-Id")
		accessKeySecret := c.GetHeader("X-Access-Key-Secret")
		if accessKeyID == "" || accessKeySecret == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing access key"})
			return
		}

		// TODO: verify with postgres hashed secret.
		c.Set("project_id", "stub-project")
		c.Next()
	}
}
