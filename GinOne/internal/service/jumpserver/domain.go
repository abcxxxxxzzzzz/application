package jumpserver

import (
	"GinOne/config"
	"GinOne/internal/model"
	"GinOne/internal/repository"
	"GinOne/pkg/cache"
	"GinOne/pkg/errcode"
	"GinOne/pkg/logger"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"gorm.io/gorm"
)

// nullCacheValue 空缓存标记，防止缓存穿透
const nullCacheValue = "null"

// nullCacheTTL 空缓存 TTL，较短以便数据创建后能快速生效
const nullCacheTTL = 60 * time.Second


type DomainService interface {
	GetByName(ctx context.Context, name string) (*model.Domain, error)
}

type domainService struct {
	repo        repository.DomainRepository
	cache       *cache.CacheWithSingleflight
	cacheExpire time.Duration
	cfg         *config.Config
}


// type tokenService struct {
// 	token DomainService
// }

// func NewDomainService(token TokenService) DomainService {
// }

func NewDomainService(repo repository.DomainRepository, c cache.Cache, expire int,  cfg *config.Config) DomainService {
	
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
		cfg:          cfg, 
	}
}


func (s *domainService) GetByName(ctx context.Context, name string) (*model.Domain, error) {

	cacheKey := fmt.Sprintf("domain:%s", name)

	// fmt.Printf("s.cache = %#v\n", s.cache)

	// 无缓存时直接查询数据库
	if s.cache == nil {
		domain, err := s.repo.GetByName(ctx, name)

		if err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return nil, errcode.ErrNotFound()
			}
			return nil, errcode.ErrInternal().Wrap(err)
		}

		return  domain, nil
	}


		// 使用 singleflight 防止缓存击穿
	cached, err := s.cache.GetOrLoad(ctx, cacheKey, func() (string, error) {
		domain, err := s.repo.GetByName(ctx, name)
		if err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				// 返回空缓存标记，防止缓存穿透
				return nullCacheValue, nil
			}
			return "", err
		}
		data, marshalErr := json.Marshal(domain)
		if marshalErr != nil {
			return "", marshalErr
		}
		return string(data), nil
	}, s.cacheExpire)

	if err != nil {
		return nil, errcode.ErrInternal().Wrap(err)
	}

	// 空缓存命中：该 name 不存在
	if cached == nullCacheValue {
		return nil, errcode.ErrNotFound()
	}

	var domain model.Domain
	if err := json.Unmarshal([]byte(cached), &domain); err != nil {
		logger.WithCtx(ctx).Warnw("unmarshal product cache failed", "error", err)
		return nil, errcode.ErrInternal().Wrap(err)
	}



  // b, _ := json.Marshal(domain)
  // fmt.Println(string(b))
  // fmt.Println("========== GetByName End ==========")

	return &domain, nil


}

// func (s *domainService) CreateToken(ctx context.Context, target string) (string, error) {
// 	// return s.token.Create(ctx, target)
// 	return "", nil
// }

// func (s *domainService) ValidateToken(ctx context.Context, token, target string) bool {
// 	// return s.token.Validate(ctx, token, target)
// 	return true
// }

// func (s *domainService) DecodeTarget(encoded string) (string, error) {
// 	data, err := base64.StdEncoding.DecodeString(encoded)
// 	if err != nil {
// 		return "", fmt.Errorf("invalid base64: %w", err)
// 	}

// 	return string(data), nil
// }