package errcode

// 业务错误码使用五位数字：前三位对应 HTTP 状态码，后两位预留给同类业务错误细分。
// 响应层负责将这些业务错误码映射为实际的 HTTP 状态码。
// 错误码常量，供外部按 code 值引用（如 response.ErrorWithMsg）
const (
	CodeBadRequest         = 40000
	CodeUnauthorized       = 40100
	CodeForbidden          = 40300
	CodeNotFound           = 40400
	CodeMethodNotAllowed   = 40500
	CodeTooManyRequests    = 42900
	CodeInternal           = 50000
	CodeServiceUnavailable = 50300 
	

	CodeUserOrPassword  = 20001
	CodeUserDisabled    = 20002
	CodeAdminOrPassword = 20003
	CodeAdminDisabled   = 20004

	// CodeProductNotFound = 20101
	// CodeProductOffShelf = 20102
	// CodeStockNotEnough  = 20103
	// CodeAmountLimit     = 20104
)

// 通用错误码 10001-19999
// 每次调用返回新实例，避免全局指针被意外修改

func ErrBadRequest() *AppError {
	return &AppError{Code: CodeBadRequest, Message: "请求参数错误", httpStatus: 400}
}

func ErrUnauthorized() *AppError {
	return &AppError{Code: CodeUnauthorized, Message: "未授权", httpStatus: 401}
}

func ErrForbidden() *AppError {
	return &AppError{Code: CodeForbidden, Message: "禁止访问", httpStatus: 403}
}

func ErrNotFound() *AppError {
	return &AppError{Code: CodeNotFound, Message: "资源不存在", httpStatus: 404}
}

func ErrInternal() *AppError {
	return &AppError{Code: CodeInternal, Message: "服务器内部错误", httpStatus: 500}
}

func ErrTooManyRequests() *AppError {
	return &AppError{Code: CodeTooManyRequests, Message: "请求过于频繁", httpStatus: 429}
}

// 用户错误码 20001-20099

func ErrUserOrPassword() *AppError {
	return &AppError{Code: CodeUserOrPassword, Message: "用户名或密码错误", httpStatus: 401}
}

func ErrUserDisabled() *AppError {
	return &AppError{Code: CodeUserDisabled, Message: "用户已被禁用", httpStatus: 403}
}

func ErrAdminOrPassword() *AppError {
	return &AppError{Code: CodeAdminOrPassword, Message: "管理员账号或密码错误", httpStatus: 401}
}

func ErrAdminDisabled() *AppError {
	return &AppError{Code: CodeAdminDisabled, Message: "管理员账号已被禁用", httpStatus: 403}
}

