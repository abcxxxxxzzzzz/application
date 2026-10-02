package migration

import (
	"GinOne/internal/model"
	"GinOne/pkg/logger"
	"fmt"

	"gorm.io/gorm"
)

// AutoMigrate 自动迁移数据库表结构，返回 error 让调用方统一处理
func AutoMigrate(db *gorm.DB) error {
	err := db.AutoMigrate(
		&model.Domain{},
		&model.DomainPool{},
		&model.Group{},
	)
	if err != nil {
		return fmt.Errorf("auto migrate failed: %w", err)
	}
	logger.Log.Info("database migration completed")
	return nil
}