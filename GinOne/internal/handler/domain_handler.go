package handler

import (
	"GinOne/pkg/errcode"
	"GinOne/pkg/response"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	htmltemplate "html/template"
	"strings"
	texttemplate "text/template"

	"github.com/gin-gonic/gin"
)

type domainService interface {
	// SearchDomainData(ctx context.Context)
}

type DomainHandler struct {
	domainSvc domainService
	index     *htmltemplate.Template
	js        *texttemplate.Template
}

func NewDomainHandler(domainSvc domainService) *DomainHandler {
	return &DomainHandler{
		domainSvc: domainSvc,
		index: htmltemplate.Must(
			htmltemplate.ParseFiles("internal/view/templates/index.html"),
		),
		js: texttemplate.Must(
			texttemplate.ParseFiles("internal/view/templates/jump.js"),
		),
	}
}


// 第一跳 定义模板数据
type FirstJumpData struct {
    JSURLsJSON template.JS
    Nonce      string
}

func buildJSURLsJSON() (template.JS, error) {
    domains := []string{
				"example1.com",
				"example2.com",
        "43.163.238.95:8323",
        
    }

    data, err := json.Marshal(domains)
    if err != nil {
        return "", err
    }

    return template.JS(`"` + base64.RawStdEncoding.EncodeToString(data) + `"`), nil
}



func generateNonce() (string, error) {
    b := make([]byte, 16)

    if _, err := rand.Read(b); err != nil {
        return "", err
    }

    return base64.RawURLEncoding.EncodeToString(b), nil
}

// 第一跳逻辑
func (h *DomainHandler) FirstJump(c *gin.Context) {
    jsURLsJSON, err := buildJSURLsJSON()
    if err != nil {
        response.Error(c, errcode.ErrBadRequest(), err.Error())
        return
    }

    nonce, err := generateNonce()
    if err != nil {
        response.Error(c, errcode.ErrBadRequest(), err.Error())
        return
    }

    data := FirstJumpData{
        JSURLsJSON: jsURLsJSON,
        Nonce:      nonce,
    }

    tmpl, err := template.ParseFiles("internal/view/templates/index.html")
    if err != nil {
        response.Error(c, errcode.ErrBadRequest(), err.Error())
        return
    }

    c.Header(
        "Content-Security-Policy",
        fmt.Sprintf("script-src 'self' 'nonce-%s'", nonce),
    )

    c.Header("Content-Type", "text/html; charset=utf-8")

    if err := tmpl.Execute(c.Writer, data); err != nil {
        fmt.Println("template execute error:", err)
        return
    }
}





// ==================================== SecondJump


type SecondJumpData struct {
	TargetCode1 string
	TargetCode2 string
	URLs        string
}

func (h *DomainHandler) SecondJump(c *gin.Context) {
	param, err := ParseURLParam(c)
	if err != nil {
		response.Error(c, errcode.ErrBadRequest(), err.Error())
		return
	}

	target := param.Value

	if !strings.HasPrefix(target, "http://") &&
		!strings.HasPrefix(target, "https://") {
		target = "https://" + target
	}

	targetCode1 := base64.StdEncoding.EncodeToString(
		[]byte("window.location.href="),
	)

	targetCode2 := base64.StdEncoding.EncodeToString(
		[]byte(target),
	)

	urls := []string{
		"http://example.com/kb/tgw/?channelCode=guanfang",
		"http://example2.com/kb/tgw/?channelCode=guanfang",
		"http://example3.com/kb/tgw/?channelCode=guanfang",
	}

	data := SecondJumpData{
		TargetCode1: targetCode1,
		TargetCode2: targetCode2,
		URLs:        strings.Join(urls, "|+|"),
	}

	c.Header("Content-Type", "text/html; charset=utf-8")

	if err := h.js.Execute(c.Writer, data); err != nil {
		fmt.Println("template execute error:", err)
		return
	}
}

// -----------------------------------------------------------------------
//? 前面的路径必须严格是 api.2.JS
//区分大小写
//? 后必须是 类型,Base64
//类型例如 1
//Base64 必须合法
//解码后得到实际内容



type URLParam struct {
	Type    string
	Encoded string
	Value   string
}

func ParseURLParam(c *gin.Context) (*URLParam, error) {
	// fmt.Println("========== ParseURLParam ==========")
	// fmt.Printf("RequestURI: %q\n", c.Request.RequestURI)
	// fmt.Printf("URL.Path:   %q\n", c.Request.URL.Path)
	// fmt.Printf("RawPath:    %q\n", c.Request.URL.RawPath)
	// fmt.Printf("RawQuery:   %q\n", c.Request.URL.RawQuery)
	// fmt.Println("===================================")


	rawQuery := c.Request.URL.RawQuery

	parts := strings.SplitN(rawQuery, ",", 2)
	if len(parts) != 2 {
		return nil, errors.New("invalid query format")
	}

	if parts[0] != "1" {
		return nil, errors.New("invalid type")
	}

	if parts[1] == "" {
		return nil, errors.New("empty value")
	}

	decoded, err := base64.StdEncoding.DecodeString(parts[1])
	if err != nil {
		return nil, errors.New("invalid base64")
	}

	return &URLParam{
		Type:    parts[0],
		Encoded: parts[1],
		Value:   string(decoded),
	}, nil
}