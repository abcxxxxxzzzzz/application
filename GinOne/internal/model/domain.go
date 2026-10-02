package model



type Domain struct {
	BaseModel
	Domain         string       `gorm:"type:varchar(255);uniqueIndex;not null"`
	GroupID        int          `gorm:"not null;index"`
	JumpType       string       `gorm:"type:varchar(20);not null;default:direct;index"`
	JumpMethod     string       `gorm:"type:varchar(20);not null;default:redirect"`
	StatusCode     int          `gorm:"not null;default:302"`
	TargetDomain   *string      `gorm:"type:varchar(500);index"`
	UseGroupParams bool         `gorm:"not null;default:false"`
	EmbeddedCode   *string      `gorm:"type:text"`
	Enabled        bool         `gorm:"not null;default:true;index"`

	Group Group        `gorm:"foreignKey:GroupID"`
	Pool  []DomainPool `gorm:"foreignKey:DomainID;constraint:OnDelete:CASCADE;"`
}

type DomainPool struct {
	BaseModel
	DomainID     int       `gorm:"not null;index;uniqueIndex:uq_domain_pool_target"`
	TargetDomain string    `gorm:"type:varchar(500);not null;uniqueIndex:uq_domain_pool_target"`
	Weight       int       `gorm:"not null;default:1"`
	Enabled      bool      `gorm:"not null;default:true"`


	DomainObj Domain `gorm:"foreignKey:DomainID"`
}

