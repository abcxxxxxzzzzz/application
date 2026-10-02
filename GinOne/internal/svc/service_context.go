package svc

import (
	"GinOne/config"
	"GinOne/internal/repository"
	"GinOne/internal/service/jumpserver"
	"GinOne/pkg/cache"
	"GinOne/pkg/ratelimit"
	"context"
	"fmt"

	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

// ServiceContext 集中管理所有依赖，作为唯一的依赖注入容器。
// 新增模块只需在此处添加字段并在 NewServiceContext 中初始化。
type ServiceContext struct {
	Config *config.Config

	// Service 层（导出，供 handler 使用）
	DomainSvc jumpserver.DomainService


	// 限流器
	RateLimiter *ratelimit.RateLimiter


	// 基础设施（私有，防止绕过 Service 层直接操作）
	db    *gorm.DB
	redis *redis.Client
}

// NewServiceContext 根据配置和基础设施连接创建 ServiceContext，
// 完成 repo → service 的依赖接线。
func NewServiceContext(cfg *config.Config, db *gorm.DB, rdb *redis.Client) *ServiceContext {
	// Repository
	domainRepo := repository.NewDomainRepo(db)


	// Cache（统一通过接口注入 service 层，解耦 Redis 具体实现）
	var domainCache cache.Cache
	if rdb != nil {
		domainCache = cache.NewRedisCache(rdb)
	}

	// Service
	domainSvc := jumpserver.NewDomainService(domainRepo, domainCache, cfg.Server.CacheExpire)
	// domainSvc := service.NewUserService(userRepo, cfg)


	// 限流器
	rl := ratelimit.NewRateLimiter(rdb)

	return &ServiceContext{
		Config: cfg,

		db:    db,
		redis: rdb,

		DomainSvc: domainSvc,
		RateLimiter: rl,
	}
}

// HealthCheck 检测 MySQL 和 Redis 的真实连通性
func (sc *ServiceContext) HealthCheck(ctx context.Context) error {
	sqlDB, err := sc.db.DB()
	if err != nil {
		return fmt.Errorf("get sql.DB: %w", err)
	}
	if err := sqlDB.PingContext(ctx); err != nil {
		return fmt.Errorf("mysql: %w", err)
	}
	if err := sc.redis.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("redis: %w", err)
	}
	return nil
}