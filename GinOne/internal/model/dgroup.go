package model

type Group struct {
	BaseModel
	Name         string    `json:"name" gorm:"type:varchar(100);uniqueIndex;not null"`
	CustomParams *string   `json:"custom_params" gorm:"type:varchar(1000)"`


	Domains []Domain `json:"domains" gorm:"foreignKey:GroupID;constraint:OnDelete:RESTRICT;"`
}
