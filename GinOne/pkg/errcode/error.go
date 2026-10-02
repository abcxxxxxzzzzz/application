package errcode

import "fmt"

// AppError 统一业务错误类型。
// cause 字段保存原始错误，用于日志记录但不暴露给客户端。
type AppError struct {
	Code       int    `json:"code"`
	Message    string `json:"message"`
	httpStatus int
	cause      error // 原始错误，仅用于内部日志，不序列化到响应
}

func (e *AppError) Error() string {
	if e.cause != nil {
		return fmt.Sprintf("code: %d, message: %s, cause: %v", e.Code, e.Message, e.cause)
	}
	return fmt.Sprintf("code: %d, message: %s", e.Code, e.Message)
}

// Unwrap 支持 errors.Is / errors.As 链式解包
func (e *AppError) Unwrap() error {
	return e.cause
}

func (e *AppError) HTTPStatus() int {
	return e.httpStatus
}

// Cause 返回被包装的原始错误，用于日志记录
func (e *AppError) Cause() error {
	return e.cause
}

// Wrap 在 AppError 上附加原始错误，供 service 层使用。
// 原始错误会被记录到日志，但不会暴露给客户端。
func (e *AppError) Wrap(cause error) *AppError {
	e.cause = cause
	return e
}

// New 创建自定义错误
func New(code int, httpStatus int, msg string) *AppError {
	return &AppError{Code: code, httpStatus: httpStatus, Message: msg}
}