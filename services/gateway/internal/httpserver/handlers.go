package httpserver

import (
	"io"

	"github.com/gin-gonic/gin"
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
