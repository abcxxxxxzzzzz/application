package router

import (
	"GinOne/internal/handler"
	"GinOne/internal/middleware"
	"GinOne/internal/svc"
	"GinOne/pkg/response"
	"context"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// Setup 接收 ServiceContext，内部创建所有 handler 并注册路由。
// 新增模块只需在此处添加 handler 和路由，无需修改函数签名。
func Setup(svcCtx *svc.ServiceContext, auth *middleware.AuthMiddleware) *gin.Engine {
	r := gin.New()

	// 全局中间件
	r.Use(middleware.SecurityHeaders()) // 安全响应头
	r.Use(middleware.RequestID())
	r.Use(middleware.ReqRespLogger()) // 记录请求和响应详情
	r.Use(middleware.Recovery())
	r.Use(middleware.CORS(svcCtx.Config.CORS.AllowedOrigins))
	r.Use(middleware.MaxBodySize(4 << 20)) // 4MB 请求体上限，防止 OOM

	// 健康检查：检测 MySQL 和 Redis 的真实连通性
	{
		var mu sync.RWMutex
		var last time.Time
		var lastOK bool
		var lastErr error
		const cacheTTL = time.Second
		r.GET("/health", func(c *gin.Context) {
			now := time.Now()
			mu.RLock()
			cachedLast := last
			cachedOK := lastOK
			cachedErr := lastErr
			mu.RUnlock()
			if now.Sub(cachedLast) < cacheTTL {
				if cachedOK {
					response.Success(c, gin.H{"status": "ok", "cached": true})
				} else {
					c.JSON(http.StatusServiceUnavailable, response.Response{
						Code:    -1,
						Message: "unhealthy: " + cachedErr.Error(),
					})
				}
				return
			}
			ctx, cancel := context.WithTimeout(c.Request.Context(), 3*time.Second)
			defer cancel()
			err := svcCtx.HealthCheck(ctx)
			mu.Lock()
			last = now
			lastOK = err == nil
			lastErr = err
			mu.Unlock()
			if err != nil {
				c.JSON(http.StatusServiceUnavailable, response.Response{
					Code:    -1,
					Message: "unhealthy: " + err.Error(),
				})
				return
			}
			response.Success(c, gin.H{"status": "ok"})
		})
	}

	// 创建 handler（从 ServiceContext 获取依赖）
	domainHandler := handler.NewDomainHandler(svcCtx.DomainSvc, svcCtx.Config)


	// App 客户端接口
	appGroup := r.Group("/app/v1")

	// App 域名接口
	appDomainGroup := appGroup.Group("")
	RegisterDomainRoutes(appDomainGroup, domainHandler)



	return r
}