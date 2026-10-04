package model



type Domain struct {
	BaseModel
	Domain         string       `json:"domain" gorm:"type:varchar(255);uniqueIndex;not null"`
	GroupID        int          `json:"group_id" gorm:"not null;index"`
	JumpType       string       `json:"jump_type" gorm:"type:varchar(20);not null;default:direct;index"`
	JumpMethod     string       `json:"jump_method" gorm:"type:varchar(20);not null;default:redirect"`
	StatusCode     int          `json:"status_code" gorm:"not null;default:302"`
	TargetDomain   *string      `json:"target_domain" gorm:"type:varchar(500);index"`
	UseGroupParams bool         `json:"use_group_params" gorm:"not null;default:false"`
	EmbeddedCode   *string      `json:"embedded_code" gorm:"type:text"`
	Enabled        bool         `json:"enabled" gorm:"not null;default:true;index"`

	Group Group        `json:"domain_group" gorm:"foreignKey:GroupID"`
	Pool  []DomainPool `json:"domain_pool" gorm:"foreignKey:DomainID;constraint:OnDelete:CASCADE;"`
}

type DomainPool struct {
	BaseModel
	DomainID     int       `json:"domain_id" gorm:"not null;index;uniqueIndex:uq_domain_pool_target"`
	TargetDomain string    `json:"target_domain" gorm:"type:varchar(500);not null;uniqueIndex:uq_domain_pool_target"`
	Weight       int       `json:"weight" gorm:"not null;default:1"`
	Enabled      bool      `json:"enabled" gorm:"not null;default:true"`


	DomainObj Domain `json:"domain_obj" gorm:"foreignKey:DomainID"`
}

