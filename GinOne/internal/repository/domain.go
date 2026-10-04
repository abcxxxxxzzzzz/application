package repository

import (
	database "GinOne/internal/core"
	"GinOne/internal/model"
	"context"

	"gorm.io/gorm"
)

type DomainRepository interface {
	GetByName(ctx context.Context, name string) (*model.Domain, error)
}

type domainRepo struct {
	db *gorm.DB
}

func NewDomainRepo(db *gorm.DB) DomainRepository {
	return &domainRepo{db: db}
}



// GetByName 根据 Domain 查询域名
func (r *domainRepo) GetByName(ctx context.Context, name string) (*model.Domain, error) {


	// fmt.Println("==================== repo start =================")
	// fmt.Println("==================== repo start =================")
	var domain model.Domain
	db := database.GetDB(ctx, r.db)

	// if err := db.Where("domain = ?", name).First(&domain).Error; err != nil {
	// 	return nil, err
	// }

	if err := db.
        Preload("Group").
        Preload("Pool").
        Where("domain = ? AND jump_type = ? AND enabled = ?", name, "random", true).
        First(&domain).Error; err != nil {
        return nil, err
    }

	return &domain, nil
}

