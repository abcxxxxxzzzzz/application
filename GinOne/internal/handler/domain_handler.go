package handler

import (
	"GinOne/config"
	"GinOne/internal/model"
	"GinOne/pkg/errcode"
	"GinOne/pkg/response"
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	htmltemplate "html/template"
	"net"
	"strings"
	texttemplate "text/template"

	"github.com/gin-gonic/gin"

	"GinOne/internal/view"
)





type domainService interface {
	GetByName(ctx context.Context, name string) (*model.Domain, error)
}

type DomainHandler struct {
	domainSvc domainService
	index     *htmltemplate.Template
	js        *texttemplate.Template
	cfg       *config.Config
}

func NewDomainHandler(domainSvc domainService, cfg *config.Config) *DomainHandler {
	return &DomainHandler{
		domainSvc: domainSvc,
		cfg:       cfg,
		index: htmltemplate.Must(
			// htmltemplate.ParseFiles("internal/view/templates/index.html"),
			htmltemplate.ParseFS(view.Templates, "templates/index.html"),
		),
		js: texttemplate.Must(
			// texttemplate.ParseFiles("internal/view/templates/jump.js"),
			texttemplate.ParseFS(view.Templates, "templates/jump.js"),
		),
	}
}


// 第一跳 定义模板数据
type FirstJumpData struct {
    JSURLsJSON template.JS
    Nonce      string
}

func buildJSURLsJSON(domains []string) (template.JS, error) {
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
	  // fmt.Printf("DEBUG START =====================\n")
		// a := h.cfg.Jump.FirstDomain
		// fmt.Printf("DEBUG Jump=%s\n", a)
		// // fmt.Printf("DEBUG FirstDomain=%#v\n", &h.cfg.Jump.FirstDomain)
		// fmt.Printf("DEBUG END =====================\n")

		
		// 1. 获取 host 域名
		host := c.Request.Host
		if hs, _, err := net.SplitHostPort(host); err == nil {
			host = hs
		}

		// 2. 调用 svc 上方法 GetByName， 查询是否存在这个域名
		_, err := h.domainSvc.GetByName(c.Request.Context(), host)
		if err != nil {
			response.Error(c,  errcode.ErrNotFound(), err.Error())
			return
		}

		// 3. 通过配置文件组合中间页域名
    jsURLsJSON, err := buildJSURLsJSON(h.cfg.Jump.FirstDomain)
    if err != nil {
        response.Error(c, errcode.ErrBadRequest(), err.Error())
        return
    }

		// 4. 加密一下
    nonce, err := generateNonce()
    if err != nil {
        response.Error(c, errcode.ErrBadRequest(), err.Error())
        return
    }

		// 5. 定义 temp 响应结构数据
    data := FirstJumpData{
        JSURLsJSON: jsURLsJSON,
        Nonce:      nonce,
    }

    // tmpl, err := template.ParseFiles("internal/view/templates/index.html")
    // if err != nil {
    //     response.Error(c, errcode.ErrBadRequest(), err.Error())
    //     return
    // }

    c.Header(
        "Content-Security-Policy",
        fmt.Sprintf("script-src 'self' 'nonce-%s'", nonce),
    )

    c.Header("Content-Type", "text/html; charset=utf-8")

		if err := h.index.Execute(c.Writer, data); err != nil {
			fmt.Println("template execute error:", err)
			return
		}

    // if err := tmpl.Execute(c.Writer, data); err != nil {
    //     fmt.Println("template execute error:", err)
    //     return
    // }
}





// ==================================== SecondJump


type SecondJumpData struct {
	LineCount   int
	URLs        string
}

func (h *DomainHandler) SecondJump(c *gin.Context) {
	param, err := ParseURLParam(c)


	if err != nil {
		response.Error(c, errcode.ErrBadRequest(), err.Error())
		return
	}


	// 先通过 DB 查询拼接
	domain, err := h.domainSvc.GetByName(c.Request.Context(), param.Value)

	if err != nil {
		return
	}


	targets := make([]string, 0, len(domain.Pool))

	for _, pool := range domain.Pool {
    if !pool.Enabled || pool.TargetDomain == "" {
        continue
    }

    target := pool.TargetDomain

    if domain.UseGroupParams &&
        domain.Group.CustomParams != nil &&
        *domain.Group.CustomParams != "" {
        target = appendParams(target, *domain.Group.CustomParams)
    }

    targets = append(targets, target)
	}

	data := SecondJumpData{
		URLs:        strings.Join(targets, "|+|"),
		LineCount:   len(targets),
	}

	c.Header("Content-Type", "text/html; charset=utf-8")
	c.Status(domain.StatusCode)


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






func appendParams(target, params string) string {
    if params == "" {
        return target
    }

    if strings.Contains(target, "?") {
        return target + "&" + params
    }

    return target + "?" + params
}