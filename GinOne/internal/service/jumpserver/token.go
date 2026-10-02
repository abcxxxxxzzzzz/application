package jumpserver

// import "context"

// // type JumpService interface {
// // 	CreateToken(ctx context.Con)
// // }

// type TokenService interface {
// 	Create(ctx context.Context) (string, error)
// 	Validate(ctx context.Context, token string) bool
// }

// // 验证 Token
// func IsValidToken(token string) bool {
// 	if token == "" || len(token) > 128 {
// 		return false
// 	}

// 	for _, c := range token {
// 		if !((c >= 'a' && c <= 'z') ||
// 			(c >= 'A' && c <= 'Z') ||
// 			(c >= '0' && c <= '9') ||
// 			c == '-' || c == '_') {
// 			return false
// 		}
// 	}

// 	return true
// }


