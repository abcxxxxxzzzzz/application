package router

import (
	"GinOne/internal/handler"

	"github.com/gin-gonic/gin"
)

func RegisterDomainRoutes(rg *gin.RouterGroup, h *handler.DomainHandler) {
	rg.GET("/h/*path", h.FirstJump)
	rg.GET("/api.2.JS", h.SecondJump)
}