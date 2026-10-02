package middleware

import (
	"GinOne/pkg/logger"
	"GinOne/pkg/response"
	"GinOne/pkg/utils"

	"github.com/gin-gonic/gin"
)

// HeaderRequestID 是请求链路标识使用的 HTTP 头名称。
const HeaderRequestID = "X-Request-ID"

// RequestID 读取或生成请求 ID，并写入 Gin 上下文和响应头。
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader(HeaderRequestID)
		if requestID == "" {
			requestID = utils.NewRequestID()
		}
		c.Set(response.RequestIDKey, requestID)
		c.Writer.Header().Set(HeaderRequestID, requestID)

		// 使用 logger.NewContext 一次性创建带 request_id 的 logger 并缓存到 context，
		// 后续 logger.WithCtx 直接复用，避免每次调用都分配新的 SugaredLogger。
		ctx := logger.NewContext(c.Request.Context(), requestID)
		c.Request = c.Request.WithContext(ctx)

		c.Next()
	}
}