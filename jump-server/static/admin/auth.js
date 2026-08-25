async function verifyAdmin() {

    const input =
        document.getElementById(
            "adminPassword"
        );

    const button =
        document.getElementById(
            "adminAuthButton"
        );

    const error =
        document.getElementById(
            "adminAuthError"
        );

    const password =
        input.value.trim();

    if (!password) {

        error.textContent =
            "请输入管理口令";

        error.classList.remove(
            "hidden"
        );

        input.focus();

        return;
    }

    error.classList.add(
        "hidden"
    );

    button.disabled = true;

    button.textContent =
        "验证中...";

    try {

        const response =
            await fetch(
                "/api/admin/auth/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    credentials:
                        "same-origin",

                    body:
                        JSON.stringify({
                            password,
                        }),
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "口令错误"
            );
        }

        // // 验证成功
        // document
        //     .getElementById(
        //         "adminAuth"
        //     )
        //     .remove();

        // document
        //     .getElementById(
        //         "app"
        //     )
        //     .classList.remove(
        //         "hidden"
        //     );

        input.value = "";

        hideAdminAuth();

        showAdminApp();


        // 通知其它 JS 初始化
        if (
            typeof initAdmin ===
            "function"
        ) {
            initAdmin();
        }

    } catch (e) {

        error.textContent =
            e.message ||
            "口令错误";

        error.classList.remove(
            "hidden"
        );

        input.select();

    } finally {

        button.disabled = false;

        button.textContent =
            "进入管理后台";
    }
}



async function logoutAdmin() {

    try {

        await api(
            "/api/admin/auth/logout",
            {
                method: "POST",
            }
        );

    } catch (error) {

        console.error(
            "logout error:",
            error
        );

    } finally {

        showAdminAuth();
        //  window.location.reload();
    }
}