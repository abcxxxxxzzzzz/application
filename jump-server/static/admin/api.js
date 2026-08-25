// 统一处理 API

async function api(url, options = {}) {
    const response = await fetch(url, {
        // credentials: "same-origin",
        credentials: "include",

        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });


    if (response.status === 401) {

        showAdminAuth();
        
        throw new Error(
            "登录已失效"
        );
    }



    let data;

    try {
        data = await response.json();
    } catch {
        // 非 JSON 响应
    }

    if (!response.ok) {

        let message =
            "请求失败";

        if (data?.detail) {

            // FastAPI:
            // detail: "xxx"
            if (
                typeof data.detail ===
                "string"
            ) {

                message =
                    data.detail;

            }

            // FastAPI:
            // detail: {
            //   message: "...",
            //   domains: [...]
            // }
            else if (
                typeof data.detail ===
                "object"
            ) {

                if (
                    data.detail.message
                ) {

                    message =
                        data.detail.message;

                    if (
                        Array.isArray(
                            data.detail.domains
                        ) &&
                        data.detail.domains.length
                    ) {

                        message +=
                            "\n\n已存在域名：\n" +
                            data.detail.domains.join(
                                "\n"
                            );
                    }

                } else {

                    message =
                        JSON.stringify(
                            data.detail
                        );
                }

            }

        } else if (data?.message) {

            message =
                data.message;

        }

        throw new Error(
            message
        );
    }

    return data;
}