package model

type Group struct {
	BaseModel
	Name         string    `gorm:"type:varchar(100);uniqueIndex;not null"`
	CustomParams *string   `gorm:"type:varchar(1000)"`


	Domains []Domain `gorm:"foreignKey:GroupID;constraint:OnDelete:RESTRICT;"`
}
