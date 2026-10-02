package jumpserver

import (
	"fmt"
	"strconv"
)


func ParseQuery(query string) (encoded, token string, err error) {
	if len(query) < 3 {
		return "", "", fmt.Errorf("invalid query")
	}

	if query[0:2] != "1," {
		return "", "", fmt.Errorf("invalid prefix")
	}

	parts := make([]string, 0, 2)
	start := 2

	for i := 2; i < len(query); i++ {
		if query[i] == ',' {
			parts = append(parts, query[start:i])
			start = i + 1
		}
	}

	parts = append(parts, query[start:])

	if len(parts) != 2 {
		return "", "", fmt.Errorf("invalid query")
	}

	encoded = parts[0]
	token = parts[1]

	if encoded == "" || !IsValidToken(token) {
		return "", "", fmt.Errorf("invalid parameter")
	}

	_ = strconv.IntSize

	return encoded, token, nil
}