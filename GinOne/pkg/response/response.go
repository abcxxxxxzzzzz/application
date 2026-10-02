package response

import (
	"GinOne/pkg/errcode"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

// RequestIDKey 是请求 ID 中间件和响应工具共享的 Gin 上下文键。
const RequestIDKey = "request_id"


// Response 统一响应结构
type Response struct {
	Code      int    `json:"code"`
	Message   string `json:"message"`
	Data      any    `json:"data,omitempty"`
	RequestID string `json:"request_id,omitempty"`
}


// Success 成功响应（支持自定义消息）； 并带上当前请求 ID
func Success(c *gin.Context, data any, messages ...string) {
	msg := "success"

	if len(messages) > 0 && messages[0] != "" {
		msg = messages[0]
	}

	c.JSON(http.StatusOK, Response{
		Code:      0,
		Message:   msg,
		Data:      data,
		RequestID: requestID(c),
	})
}



// Error 错误响应，支持自定义消息。
func Error(c *gin.Context, err *errcode.AppError, messages ...string) {
	msg := err.Message

	if len(messages) > 0 && messages[0] != "" {
		msg = messages[0]
	}

	// 将错误注入 Gin 错误链，让 Logger 中间件能够捕获并记录。
	_ = c.Error(fmt.Errorf("[%d] %s", err.Code, msg))

	c.JSON(err.HTTPStatus(), Response{
		Code:    err.Code,
		Message: msg,
	})
}




// =================================================================


// PageData 分页数据
type PageData struct {
	List  any   `json:"list"`
	Total int64 `json:"total"`
	Page  int   `json:"page"`
	Size  int   `json:"size"`
}



// SuccessWithPage 分页成功响应
func SuccessWithPage(c *gin.Context, list any, total int64, page, size int) {
	Success(c, PageData{
		List:  list,
		Total: total,
		Page:  page,
		Size:  size,
	})
}
// =================================================================






// 请求 ID,链路追踪流程
func requestID(c *gin.Context) string {
	value, exists := c.Get(RequestIDKey)
	if !exists {
		return ""
	}
	id, _ := value.(string)
	return id
}




