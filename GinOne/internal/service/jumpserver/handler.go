package jumpserver

import (
	"encoding/json"
	htmltemplate "html/template"
	"net/http"
	"strings"
	texttemplate "text/template"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	service DomainService
	index   *htmltemplate.Template
	js      *texttemplate.Template
}

type IndexData struct {
	Token      string
	JSURLsJSON string
}

type JSData struct {
	TargetJSON string
	URLsJSON   string
}

func NewHandler(
	service DomainService,
	index *htmltemplate.Template,
	js *texttemplate.Template,
) *Handler {
	return &Handler{
		service: service,
		index:   index,
		js:      js,
	}
}

func (h *Handler) Index(c *gin.Context) {
	target := c.Request.URL.String()

	token, err := h.service.CreateToken(
		c.Request.Context(),
		target,
	)
	if err != nil {
		c.String(http.StatusInternalServerError, "server error")
		return
	}

	jsURLsJSON, err := json.Marshal(Config.JSURLs)
	if err != nil {
		c.String(http.StatusInternalServerError, "server error")
		return
	}

	c.Header("Cache-Control", "no-store")

	if err := h.index.Execute(c.Writer, IndexData{
		Token:      token,
		JSURLsJSON: string(jsURLsJSON),
	}); err != nil {
		_ = c.Error(err)
	}
}

func (h *Handler) JumpJS(c *gin.Context) {
	// 严格区分大小写
	if c.Request.URL.Path != "/api.2.JS" {
		c.Status(http.StatusNotFound)
		return
	}

	// 只允许 GET
	if c.Request.Method != http.MethodGet {
		c.Status(http.StatusMethodNotAllowed)
		return
	}

	parts := strings.Split(c.Request.URL.RawQuery, ",")

	// 必须是：
	// ?1,BASE64,TOKEN
	if len(parts) != 3 || parts[0] != "1" {
		c.Status(http.StatusNotFound)
		return
	}

	encoded := parts[1]
	token := parts[2]

	if encoded == "" || !IsValidToken(token) {
		c.Status(http.StatusNotFound)
		return
	}

	// 验证 Token + BASE64
	if !h.service.ValidateToken(
		c.Request.Context(),
		token,
		encoded,
	) {
		c.Status(http.StatusNotFound)
		return
	}

	// Base64 解码
	target, err := h.service.DecodeTarget(encoded)
	if err != nil {
		c.Status(http.StatusNotFound)
		return
	}

	// Target 转 JSON，安全嵌入 JS
	targetJSON, err := json.Marshal(target)
	if err != nil {
		c.Status(http.StatusNotFound)
		return
	}

	// 二跳地址转 JSON
	urlsJSON, err := json.Marshal(Config.SecondJumpURLs)
	if err != nil {
		c.Status(http.StatusInternalServerError)
		return
	}

	c.Header(
		"Content-Type",
		"application/javascript; charset=utf-8",
	)

	c.Header(
		"Cache-Control",
		"private, no-store, no-cache, must-revalidate",
	)

	c.Header("Pragma", "no-cache")

	if err := h.js.Execute(c.Writer, JSData{
		TargetJSON: string(targetJSON),
		URLsJSON:   string(urlsJSON),
	}); err != nil {
		_ = c.Error(err)
	}
}

func IsValidToken(token string) bool {
	if token == "" || len(token) > 128 {
		return false
	}

	for _, c := range token {
		if (c >= 'a' && c <= 'z') ||
			(c >= 'A' && c <= 'Z') ||
			(c >= '0' && c <= '9') ||
			c == '-' ||
			c == '_' {
			continue
		}

		return false
	}

	return true
}