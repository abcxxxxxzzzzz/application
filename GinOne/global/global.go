package global

import (
	"GinOne/config"
	"GinOne/pkg/logger"
	"context"
	"errors"
	"fmt"
	"net/http"
	"time"

	"github.com/redis/go-redis/v9"
)

type App struct {
	cfg        *config.Config
	httpServer *http.Server
	redis      *redis.Client
}

func NewApp(cfg *config.Config, handler http.Handler, redisClient *redis.Client) *App {
	return &App{
		cfg: cfg,
		httpServer: &http.Server{
			Addr:              fmt.Sprintf(":%d", cfg.App.Port),
			Handler:           handler,
			ReadTimeout:       time.Duration(cfg.Server.ReadTimeoutSeconds) * time.Second,
			WriteTimeout:      time.Duration(cfg.Server.WriteTimeoutSeconds) * time.Second,
			ReadHeaderTimeout: 5 * time.Second,
			IdleTimeout:       60 * time.Second,
		},
		redis:    redisClient,
	}
}

func (a *App) Run(ctx context.Context) error {
	_, trimCancel := context.WithCancel(ctx)

	errCh := make(chan error, 2)

	go func() {
		logger.Log.Infof("server starting on port %d", a.cfg.App.Port)
		if err := a.httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- fmt.Errorf("http server failed: %w", err)
		}
	}()


	var runErr error
	select {
	case <-ctx.Done():
	case err := <-errCh:
		runErr = err
	}

	trimCancel()

	shutdownTimeout := 10 * time.Second
	if a.cfg.Server.ShutdownTimeoutSeconds > 0 {
		shutdownTimeout = time.Duration(a.cfg.Server.ShutdownTimeoutSeconds) * time.Second
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()



	if err := a.httpServer.Shutdown(shutdownCtx); err != nil && runErr == nil {
		runErr = fmt.Errorf("shutdown http server failed: %w", err)
	}

	return runErr
}