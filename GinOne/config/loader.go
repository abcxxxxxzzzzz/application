package config

import (
	"fmt"
	"net/url"
	"strings"

	"github.com/spf13/viper"
)

// 定义一个函数, 加载配置文件
func Load() (*Config, error) {
	v := viper.New()            // 创建 Viper 配置管理对象
	v.SetConfigName("config")   // 定义加载配置文件名字
	v.SetConfigType("yaml")     // 定义加载配置文件类型
	v.AddConfigPath("./config") // 定义加载配置文件路径， 去当前程序运行目录下面的 config 文件夹找配置

	// 读取配置文件，如果读取失败； 返回读取配置文件错误
	if err := v.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("read config failed: %w", err)
	}

	// 创建类型为 Config 结构体变量 cfg，使用它的零值初始化
	var cfg Config

	//  YAML 配置转换成 Go 结构体，
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("Unmarshal config failed: %w", err)
	}

	// 检查配置文件是否合法
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}


	// 最后返回配置
	return &cfg, nil

}


// Validate 校验配置必填项和基本约束，启动时 fail-fast。
func (c *Config) Validate() error {
	c.App.Name = strings.TrimSpace(c.App.Name)
	if c.App.Name == "" {
		return fmt.Errorf("missing configuration: app.name")
	}

	c.App.Mode = strings.ToLower(strings.TrimSpace(c.App.Mode))
	switch c.App.Mode {
	case "debug", "release", "test":
	default:
		return fmt.Errorf("invalid configuration: app.mode must be one of debug, release, test")
	}

	if c.App.Port <= 0 || c.App.Port > 65535 {
		return fmt.Errorf("invalid configuration: app.port must be between 1 and 65535")
	}

	if c.Server.ReadTimeoutSeconds <= 0 {
		return fmt.Errorf("invalid configuration: server.read_timeout_seconds must be greater than 0")
	}

	if c.Server.WriteTimeoutSeconds <= 0 {
		return fmt.Errorf("invalid configuration: server.write_timeout_seconds must be greater than 0")
	}

	if c.Server.IdleTimeoutSeconds <= 0 {
		return fmt.Errorf("invalid configuration: server.idle_timeout_seconds must be greater than 0")
	}

	switch c.Log.Level {
	case "debug", "info", "warn", "error":
	default:
		return fmt.Errorf("invalid configuration: log.level must be one of debug, info, warn, error")
	}


	c.MySQL.Host = strings.TrimSpace(c.MySQL.Host)
	if c.MySQL.Host == "" {
		return fmt.Errorf("missing configuration: mysql.host")
	}

	if c.MySQL.Port <= 0 || c.MySQL.Port > 65535 {
		return fmt.Errorf("invalid configuration: mysql.port must be between 1 and 65535")
	}

	c.MySQL.Database = strings.TrimSpace(c.MySQL.Database)
	if c.MySQL.Database == "" {
		return fmt.Errorf("missing configuration: mysql.database")
	}

	c.MySQL.Username = strings.TrimSpace(c.MySQL.Username)
	if c.MySQL.Username == "" {
		return fmt.Errorf("missing configuration: mysql.username")
	}

	if c.MySQL.Timeout <= 0 {
		return fmt.Errorf("invalid configuration: mysql.timeout must be greater than 0")
	}

	if c.MySQL.MaxOpenConns < 0 {
		return fmt.Errorf("invalid configuration: mysql.max_open_conns cannot be less than 0")
	}

	if c.MySQL.MaxIdleConns < 0 {
		return fmt.Errorf("invalid configuration: mysql.max_idle_conns cannot be less than 0")
	}

	if c.MySQL.MaxOpenConns > 0 && c.MySQL.MaxIdleConns > c.MySQL.MaxOpenConns {
		return fmt.Errorf("invalid configuration: mysql.max_idle_conns cannot be greater than mysql.max_open_conns")
	}

	if c.MySQL.MaxLifeTime < 0 {
		return fmt.Errorf("invalid configuration: mysql.conn_max_lifetime_seconds cannot be less than 0")
	}

	if c.Redis.Enabled {
		c.Redis.Host = strings.TrimSpace(c.Redis.Host)
		if c.Redis.Host == "" {
			return fmt.Errorf("missing configuration: redis.host")
		}

		if c.Redis.Port <= 0 || c.Redis.Port > 65535 {
			return fmt.Errorf("invalid configuration: redis.port must be between 1 and 65535")
		}

		if c.Redis.DB < 0 {
			return fmt.Errorf("invalid configuration: redis.db cannot be less than 0")
		}

		if c.Redis.PoolSize <= 0 {
			return fmt.Errorf("invalid configuration: redis.pool_size must be greater than 0")
		}
	}

	origins, err := normalizeCORSOrigins(c.CORS.AllowedOrigins)
	if err != nil {
		return err
	}

	c.CORS.AllowedOrigins = origins

	return nil
}





// normalizeCORSOrigins 校验并整理允许跨域访问的来源列表。
// 每个来源必须是仅包含协议、主机和可选端口的 http/https origin；
// 空值、通配符、用户信息、路径、查询参数和片段均不被允许。
// 返回结果会移除首尾空白和重复项，并保持来源首次出现的顺序。
func normalizeCORSOrigins(values []string) ([]string, error) {
	origins := make([]string, 0, len(values))
	seen := make(map[string]struct{}, len(values))

	for _, value := range values {
		origin := strings.TrimSpace(value)

		if origin == "" {
			return nil, fmt.Errorf("invalid configuration: cors.allowed_origins cannot contain empty values")
		}

		if strings.Contains(origin, "*") {
			return nil, fmt.Errorf("invalid configuration: cors.allowed_origins does not allow wildcards: %s", origin)
		}

		// A valid CORS origin must be in the form scheme://host[:port].
		// It cannot contain other URL components.
		parsed, err := url.Parse(origin)
		if err != nil ||
			(parsed.Scheme != "http" && parsed.Scheme != "https") ||
			parsed.Host == "" ||
			parsed.User != nil ||
			parsed.Path != "" ||
			parsed.RawQuery != "" ||
			parsed.Fragment != "" {
			return nil, fmt.Errorf("invalid configuration: cors.allowed_origins must be an http/https origin without a path, query, or fragment: %s", origin)
		}

		// Ignore duplicate origins to avoid generating duplicate CORS configuration.
		if _, exists := seen[origin]; exists {
			continue
		}

		seen[origin] = struct{}{}
		origins = append(origins, origin)
	}

	return origins, nil
}




