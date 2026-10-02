package jumpserver

import (
	"GinOne/internal/repository"
	"GinOne/pkg/cache"
	"context"
	"encoding/base64"
	"fmt"
	"time"
)

// nullCacheValue 空缓存标记，防止缓存穿透
const nullCacheValue = "null"

// nullCacheTTL 空缓存 TTL，较短以便数据创建后能快速生效
const nullCacheTTL = 60 * time.Second


type DomainService interface {
	CreateToken(ctx context.Context, target string) (string, error)
	ValidateToken(ctx context.Context, token, target string) bool
	DecodeTarget(encoded string) (string, error)
}

type domainService struct {
	repo        repository.DomainRepository
	cache       *cache.CacheWithSingleflight
	cacheExpire time.Duration
}


// type tokenService struct {
// 	token DomainService
// }

// func NewDomainService(token TokenService) DomainService {
// }

func NewDomainService(repo repository.DomainRepository, c cache.Cache, expire int) DomainService {
	
	if expire <= 0 {
		expire = 600 // 默认 10 分钟
	}
	var cacheWithSF *cache.CacheWithSingleflight
	if c != nil {
		cacheWithSF = cache.NewCacheWithSingleflight(c)
	}
	return &domainService{
		repo:        repo,
		cache:       cacheWithSF,
		cacheExpire: time.Duration(expire) * time.Second,
	}
}

func (s *domainService) CreateToken(ctx context.Context, target string) (string, error) {
	// return s.token.Create(ctx, target)
	return "", nil
}

func (s *domainService) ValidateToken(ctx context.Context, token, target string) bool {
	// return s.token.Validate(ctx, token, target)
	return true
}

func (s *domainService) DecodeTarget(encoded string) (string, error) {
	data, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return "", fmt.Errorf("invalid base64: %w", err)
	}

	return string(data), nil
}