package model

import (
	"time"
)

// BaseModel 公共模型字段
type BaseModel struct {
	ID              uint        `json:"id" gorm:"primaryKey;autoIncrement"`
	CreatedAt      time.Time    `json:"created_at" gorm:"not null;default:CURRENT_TIMESTAMP"`
	UpdatedAt      time.Time    `json:"updated_at" gorm:"not null;default:CURRENT_TIMESTAMP"`

	// DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`
}


