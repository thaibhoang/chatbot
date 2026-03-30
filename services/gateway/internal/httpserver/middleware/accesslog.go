package middleware

import (
	"time"

	"github.com/thaibhoang/chatbot/services/gateway/pkg/logger"
	"github.com/gin-gonic/gin"
)

func AccessLog() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		projectID, _ := c.Get("project_id")
		logger.Infof(
			"method=%s path=%s status=%d latency_ms=%d project_id=%v request_id=%s",
			c.Request.Method,
			c.Request.URL.Path,
			c.Writer.Status(),
			time.Since(start).Milliseconds(),
			projectID,
			c.GetString("request_id"),
		)
	}
}
