// package main

// import (
// 	htmltemplate "html/template"
// 	"os"
// 	texttemplate "text/template"

// 	"github.com/gin-gonic/gin"
// 	"github.com/redis/go-redis/v9"
// )

// func main() {
// 	rdb := redis.NewClient(&redis.Options{
// 		Addr: "127.0.0.1:6379",
// 	})

// 	tokenService := NewRedisTokenService(rdb)
// 	jumpService := NewJumpService(tokenService)

// 	indexTpl := htmltemplate.Must(
// 		htmltemplate.ParseFiles("templates/index.html"),
// 	)

// 	jsTpl := texttemplate.Must(
// 		texttemplate.ParseFiles("templates/jump.js"),
// 	)

// 	handler := NewHandler(
// 		jumpService,
// 		indexTpl,
// 		jsTpl,
// 	)

// 	r := gin.Default()

// 	role := os.Getenv("ROLE")

// 	switch role {
// 	case "index":
// 		// 一跳域名 A
// 		r.GET("/*path", handler.Index)

// 	case "js":
// 		// JS 域名 B/C
// 		r.GET("/api.2.JS", handler.JumpJS)

// 	default:
// 		panic("ROLE must be index or js")
// 	}

// 	if err := r.Run(":8080"); err != nil {
// 		panic(err)
// 	}
// }

package main

import (
	"GinOne/config"
	"GinOne/global"
	core "GinOne/internal/core"
	"GinOne/internal/middleware"
	"GinOne/internal/router"
	"GinOne/internal/svc"
	"GinOne/migration"
	"GinOne/pkg/logger"
	"context"
	"fmt"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
)

func main() {
	if err := run(); err != nil {
		logger.Log.Errorw("server exited with error", "error", err)
	}
	logger.Log.Info("server exited")
}


func run() error {
	// 1. 加载配置（logger.Log 已有 init() 提供的 fallback，不会 nil panic）
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("Load config: %w", err)
	}


	// 2. 初始化日志
	logger.Init(&cfg.Log)
	defer logger.Sync()


	// 3. 设置 Gin 模式
	gin.SetMode(cfg.App.Mode)


	// 4. 初始化 MySQL
	db, err := core.InitMySQL(&cfg.MySQL, &cfg.Log)
	if err != nil {
		return fmt.Errorf("init mysql: %w", err)
	}
	defer core.CloseMySQL(db)


	// 5. 初始化 Redis
	rdb, err := core.InitRedis(&cfg.Redis, &cfg.Log)
	if err != nil {
		return fmt.Errorf("init redis: %w", err)
	}
	defer core.CloseRedis(rdb)


	// 6. 数据库迁移（可配置）
	if cfg.App.AutoMigrate {
		if err := migration.AutoMigrate(db); err != nil {
			return fmt.Errorf("auto migrate: %w", err)
		}
	}


	// 7. 初始化 JWT
	authMiddleware := middleware.NewAuthMiddleware(cfg.JWT.Secret)


	// 11. 初始化 ServiceContext（一行完成所有依赖接线）
	svcCtx := svc.NewServiceContext(cfg, db, rdb)

	// 12. 路由（只传 ServiceContext）
	r := router.Setup(svcCtx, authMiddleware)
	
	app := global.NewApp(cfg, r, rdb)

	runCtx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := app.Run(runCtx); err != nil {
		return fmt.Errorf("run app: %w", err)
	}

	return nil
}