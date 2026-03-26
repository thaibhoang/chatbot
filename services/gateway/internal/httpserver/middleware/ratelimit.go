package middleware

import (
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

type bucket struct {
	lastRefill time.Time
	tokens     int
}

func RateLimit(rps int) gin.HandlerFunc {
	if rps <= 0 {
		rps = 20
	}
	var (
		mu      sync.Mutex
		buckets = map[string]*bucket{}
	)

	return func(c *gin.Context) {
		key := c.ClientIP()
		now := time.Now()

		mu.Lock()
		b, ok := buckets[key]
		if !ok {
			b = &bucket{lastRefill: now, tokens: rps}
			buckets[key] = b
		}

		if now.Sub(b.lastRefill) >= time.Second {
			b.tokens = rps
			b.lastRefill = now
		}

		if b.tokens <= 0 {
			mu.Unlock()
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "rate limit exceeded"})
			return
		}
		b.tokens--
		mu.Unlock()

		c.Next()
	}
}
