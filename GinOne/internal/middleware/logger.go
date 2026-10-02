package middleware

import (
	"GinOne/pkg/logger"
	"time"

	"github.com/gin-gonic/gin"
)

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		fields := []interface{}{
			"method", c.Request.Method,
			"path", path,
			"query", query,
			"status", status,
			"latency", latency.String(),
			"ip", c.ClientIP(),
			"user_agent", c.Request.UserAgent(),
		}

		// 如果 handler 通过 c.Error() 注入了错误，一并记录
		if len(c.Errors) > 0 {
			fields = append(fields, "errors", c.Errors.String())
		}

		log := logger.WithCtx(c.Request.Context())

		switch {
		case status >= 500:
			log.Errorw("request", fields...)
		case status >= 400:
			log.Warnw("request", fields...)
		default:
			log.Infow("request", fields...)
		}
	}
}