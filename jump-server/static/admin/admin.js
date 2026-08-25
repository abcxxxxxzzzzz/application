
function renderPageInfo() {

    document.getElementById(
        "pageInfo"
    ).textContent =
        `第 ${state.page} / ${state.totalPages} 页`;

    document.getElementById(
        "totalInfo"
    ).textContent =
        `共 ${state.total} 条`;

    document.getElementById(
        "pageSizeSelect"
    ).value =
        String(state.pageSize);
}


function changePage(step) {

    const page =
        state.page + step;

    if (
        page < 1 ||
        page > state.totalPages
    ) {
        return;
    }

    state.page =
        page;

    loadDomains();
}

function resetSearch() {

    document.getElementById(
        "searchInput"
    ).value = "";

    document.getElementById(
        "groupFilter"
    ).value = "";

    document.getElementById(
        "typeFilter"
    ).value = "";

    document.getElementById(
        "enabledFilter"
    ).value = "";

    state.page = 1;

    loadDomains();
}

// document.addEventListener(
//     "DOMContentLoaded",
//     async () => {

//         try {

//             await loadGroups();
//             await loadDomains();

//         } catch (error) {

//             showToast(
//                 error.message,
//                 false
//             );
//         }

//         const batchDomains =
//             document.getElementById(
//                 "batchDomains"
//             );

//         if (batchDomains) {

//             batchDomains.addEventListener(
//                 "input",
//                 function () {

//                     const count =
//                         parseDomains(
//                             this.value
//                         ).length;

//                     const counter =
//                         document.getElementById(
//                             "batchDomainCount"
//                         );

//                     if (counter) {

//                         counter.textContent =
//                             `${count} 个域名`;
//                     }
//                 }
//             );
//         }
//     }
// );

// 需认证

function showAdminApp() {

    const app =
        document.getElementById("app");

    const body =
        document.getElementById("adminBody");

    if (app) {
        app.classList.remove("hidden");
    }

    if (body) {
        body.classList.remove("overflow-hidden");
    }
}


function hideAdminApp() {

    const app =
        document.getElementById("app");

    const body =
        document.getElementById("adminBody");

    if (app) {
        app.classList.add("hidden");
    }

    if (body) {
        body.classList.add("overflow-hidden");
    }
}


function showAdminAuth() {

    hideAdminApp();

    const auth =
        document.getElementById("adminAuth");

    if (auth) {
        auth.classList.remove("hidden");
    }

    setTimeout(() => {
        document
            .getElementById("adminPassword")
            ?.focus();
    }, 50);
}


function hideAdminAuth() {

    document
        .getElementById("adminAuth")
        ?.classList.add("hidden");
}



function showAdminAuthError(message) {

    const el =
        document.getElementById(
            "adminAuthError"
        );

    if (!el) return;

    el.textContent = message;

    el.classList.remove("hidden");
}


function clearAdminAuthError() {

    const el =
        document.getElementById(
            "adminAuthError"
        );

    if (!el) return;

    el.textContent = "";

    el.classList.add("hidden");
}




async function checkAdminAuth() {

    try {

        await api(
            "/api/admin/auth/check",
            {
                method: "POST",
            }
        );

        return true;

    } catch (error) {

        if (error.status === 401) {
            openAdminLoginModal();
            return false;
        }

        throw error;
    }
}


async function initAdmin() {
// // 默认显示验证层
//     showAdminAuth();
    // 初始状态：整个后台隐藏
    hideAdminApp();
    hideAdminAuth();

    try {

        // 先验证口令
        await checkAdminAuth();

        // Cookie 有效
        // hideAdminAuth();
        // 已登录
        showAdminApp();

        // 已登录
        // document
        //     .getElementById("app")
        //     .classList.remove("hidden");

        // 登录成功后再加载数据
        await loadGroups();
        await loadDomains();

        // 批量添加域名数量
        const batchDomains =
            document.getElementById(
                "batchDomains"
            );

        if (batchDomains) {

            batchDomains.addEventListener(
                "input",
                function () {

                    const count =
                        parseDomains(
                            this.value
                        ).length;

                    const counter =
                        document.getElementById(
                            "batchDomainCount"
                        );

                    if (counter) {
                        counter.textContent =
                            `${count} 个域名`;
                    }
                }
            );
        }

    } catch (error) {


        // 401
        showAdminAuth();

        clearAdminAuthError();
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {
        initAdmin();
    }
);