package repository

import (
	database "GinOne/internal/core"
	"GinOne/internal/model"
	"context"

	"gorm.io/gorm"
)

type DomainRepository interface {
	GetByID(ctx context.Context, id uint) (*model.Domain, error)
}

type domainRepo struct {
	db *gorm.DB
}

func NewDomainRepo(db *gorm.DB) DomainRepository {
	return &domainRepo{db: db}
}



// GetByID 根据 ID 查询商品
func (r *domainRepo) GetByID(ctx context.Context, id uint) (*model.Domain, error) {
	var domain model.Domain
	db := database.GetDB(ctx, r.db)
	if err := db.First(&domain, id).Error; err != nil {
		return nil, err
	}
	return &domain, nil
}

