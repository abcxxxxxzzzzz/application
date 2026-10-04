package config

// Config 汇总服务启动和运行所需的全部配置。
type Config struct {
	App        AppConfig    `mapstructure:"app"`
	Server     ServerConfig `mapstructure:"server"`
	Log        LogConfig    `mapstructure:"log"`
	MySQL      MySQLConfig  `mapstructure:"mysql"`
	Redis      RedisConfig  `mapstructure:"redis"`
	JWT        JWTConfig    `mapstructure:"jwt"`
	CORS       CORSConfig   `mapstructure:"cors"`
	
	// Cron       CronConfig   `mapstructure:"cron"`
	// ConfigPath string       `mapstructure:"-"`
	// BaseDir    string       `mapstructure:"-"`
	Jump       JumpConfig   `mapstructure:"jump"`
}



// AppConfig 描述应用标识、运行模式和监听端口。
type AppConfig struct {
	Name          string  `mapstructure:"name"`
	Mode          string  `mapstructure:"mode"`
	Port          int  `mapstructure:"port"`
	AutoMigrate   bool   `mapstructure:"auto_migrate"`
}



// ServerConfig 描述 HTTP 服务器的超时参数。
type ServerConfig struct {
	ReadTimeoutSeconds  int  `mapstructure:"read_timeout_seconds"`
	WriteTimeoutSeconds int  `mapstructure:"write_timeout_seconds"`
	IdleTimeoutSeconds  int  `mapstructure:"idle_timeout_seconds"`
	ShutdownTimeoutSeconds     int  `mapstructure:"shutdown_timeout_seconds"`
	CacheExpire         int      `mapstructure:"cache_expire"`
}



// LogConfig 描述日志目录、级别和输出方式。
type LogConfig struct {
	Mode       string `mapstructure:"mode"`
	Level      string `mapstructure:"level"`
	SQLLevel   string `mapstructure:"sql_level"`
	LogDir     string `mapstructure:"log_dir"`     // 日志目录，空则不写文件；warn.log/error.log 写入此目录
	MaxSize    int    `mapstructure:"max_size"`    // 单文件最大 MB，默认 100
	MaxBackups int    `mapstructure:"max_backups"` // 保留旧文件数，默认 7
	MaxAge     int    `mapstructure:"max_age"`     // 保留天数，默认 30
	Compress   bool   `mapstructure:"compress"`    // 是否压缩归档
}



// MySQLConfig 描述 MySQL 连接和连接池参数。
type MySQLConfig struct {
	Host                    string  `mapstructure:"host"`
	Port                    int     `mapstructure:"port"`
	Database                string  `mapstructure:"database"`
	Username                string  `mapstructure:"username"`
	Password                string  `mapstructure:"password"`
	Timeout                 int     `mapstructure:"timeout"`
	Params                  string  `mapstructure:"params"`
	MaxOpenConns            int     `mapstructure:"max_open_conns"`
	MaxIdleConns            int     `mapstructure:"max_idle_conns"`
	MaxLifeTime             int     `mapstructure:"conn_max_lifetime_seconds"`
	ConnMaxIdleTime         int     `mapstructure:"conn_max_idle_time"`
	DialTimeout             int     `mapstructure:"dial_timeout"`
	ReadTimeout             int     `mapstructure:"read_timeout"`
	WriteTimeout            int     `mapstructure:"write_timeout"`
	PingTimeout             int     `mapstructure:"ping_timeout"`
	LogSQL                  bool    `mapstructure:"log_sql"`

	// GORM 性能优化
	PrepareStmt             bool    `mapstructure:"prepare_stmt"`
	SkipDefaultTransaction  bool    `mapstructure:"skip_default_transaction"`
}



// RedisConfig 描述可选 Redis 客户端及其连接池参数。
type RedisConfig struct {
	Enabled            bool    `mapstructure:"enabled"`
	Host               string  `mapstructure:"host"`
	Port               int     `mapstructure:"port"`
	Password           string  `mapstructure:"password"`
	DB                 int     `mapstructure:"db"`
	PoolSize           int     `mapstructure:"pool_size"`
	MinIdleConns       int     `mapstructure:"min_idle_conns"`
	MaxIdleConns       int     `mapstructure:"max_idle_conns"`
	PoolTimeout        int     `mapstructure:"pool_timeout"`
	DialTimeout        int     `mapstructure:"dial_timeout"`
	ReadTimeout        int     `mapstructure:"read_timeout"`
	WriteTimeout       int     `mapstructure:"write_timeout"`
	ConnMaxIdleTime    int     `mapstructure:"conn_max_idle_time"`
	ConnMaxLifetime    int     `mapstructure:"conn_max_lifetime"`
	PingTimeout        int     `mapstructure:"ping_timeout"`

	// 自动重试
	MaxRetries         int     `mapstructure:"max_retries"`
	MinRetryBackoff    int     `mapstructure:"min_retry_backoff"`
	MaxRetryBackoff    int     `mapstructure:"max_retry_backoff"`
}



// JWTConfig 权限认证KEY,时效策略
type JWTConfig struct {
	Secret string  `mapstructure:"secret"`
	Expire int     `mapstructure:"expire"`
}



// CORSConfig 描述允许跨域访问的来源和凭证策略。
type CORSConfig struct {
	AllowedOrigins   []string  `mapstructure:"allowed_origins"`
	AllowCredentials bool      `mapstructure:"allow_credentials"`
}



// jumpserver 配置
type JumpConfig struct {
	FirstDomain []string `mapstructure:"first_domain"`
}