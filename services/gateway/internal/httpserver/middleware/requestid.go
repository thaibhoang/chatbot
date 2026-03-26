package middleware

import (
	"github.com/gin-gonic/gin"
)

func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("X-Request-Id", c.GetHeader("X-Request-Id"))
		c.Next()
	}
}
