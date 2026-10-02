package ratelimit

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

// RateLimiter 基于 Redis 的限流器
type RateLimiter struct {
	rdb *redis.Client
}

var (
	ErrInvalidLimit  = errors.New("invalid limit")
	ErrInvalidWindow = errors.New("invalid window")
)

// NewRateLimiter 创建限流器
func NewRateLimiter(rdb *redis.Client) *RateLimiter {
	return &RateLimiter{rdb: rdb}
}

// Lua 脚本实现原子限流（固定窗口算法）
// KEYS[1]: 限流标识符（如 ip + route）
// ARGV[1]: 限制请求次数
// ARGV[2]: 时间窗口大小（秒）
var limitLuaScript = redis.NewScript(`
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local windowMs = tonumber(ARGV[2])

local current = redis.call('INCR', key)
if current == 1 then
    redis.call('PEXPIRE', key, windowMs)
end

local ttl = redis.call('PTTL', key)
if ttl < 0 then
    ttl = windowMs
end

if current > limit then
    return {0, ttl}
end
return {1, ttl}
`)

// Allow 判断是否允许请求
func (l *RateLimiter) Allow(ctx context.Context, key string, limit int, window time.Duration) (bool, time.Duration, error) {
	if limit <= 0 {
		return false, 0, ErrInvalidLimit
	}
	if window <= 0 {
		return false, 0, ErrInvalidWindow
	}
	windowMs := window.Milliseconds()
	if windowMs <= 0 {
		windowMs = 1
	}
	result, err := limitLuaScript.Run(ctx, l.rdb, []string{key}, limit, windowMs).Int64Slice()
	if err != nil {
		return false, 0, err
	}
	if len(result) != 2 {
		return false, 0, fmt.Errorf("unexpected rate limit result length: %d", len(result))
	}
	retryAfter := time.Duration(result[1]) * time.Millisecond

	return result[0] == 1, retryAfter, nil
}

func BuildKey(ip, method, path string) string {
	method = strings.ToUpper(method)
	if method == "" {
		method = "GET"
	}
	var builder strings.Builder
	builder.Grow(len("rl:") + len(ip) + len(method) + len(path) + 2)
	builder.WriteString("rl:")
	builder.WriteString(ip)
	builder.WriteByte(':')
	builder.WriteString(method)
	builder.WriteByte(':')
	builder.WriteString(path)
	return builder.String()
}

func RetryAfterSeconds(d time.Duration) string {
	if d <= 0 {
		return "1"
	}
	seconds := int64(d / time.Second)
	if d%time.Second != 0 {
		seconds++
	}
	if seconds <= 0 {
		seconds = 1
	}
	return strconv.FormatInt(seconds, 10)
}