let cdnAccounts = [];


// ============================================================
// 加载 Cloudflare 账号
// ============================================================

async function loadCDNAccounts() {
    try {

        const data = await apiJson(
            "/api/cdn-accounts"
        );

        if (!data) {
            return;
        }

        cdnAccounts = data;

        renderCDNAccounts();

    } catch (error) {

        console.error(error);

        alert(
            error.message || "加载 Cloudflare 账号失败"
        );
    }
}


// ============================================================
// 渲染 Cloudflare 账号
// ============================================================

function renderCDNAccounts() {

    const tbody = document.getElementById(
        "cdnAccountsTableBody"
    );

    if (!tbody) {

        console.error(
            "找不到 #cdnAccountsTableBody"
        );

        return;
    }


    if (!cdnAccounts.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="text-center text-gray-400 py-12"
                >
                    暂无 Cloudflare 账号
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = cdnAccounts
        .map(account => `

            <tr class="border-b last:border-b-0">

                <td class="px-6 py-4">
                    ${account.id}
                </td>

                <td class="px-6 py-4 font-medium">
                    ${escapeHtml(account.name)}
                </td>

                <td class="px-6 py-4 text-sm">
                    ${escapeHtml(account.account_id)}
                </td>

                <td class="px-6 py-4">

                    ${
                        account.token_configured

                            ? `
                                <span class="text-green-600">
                                    已配置
                                </span>
                            `

                            : `
                                <span class="text-red-600">
                                    未配置
                                </span>
                            `
                    }

                </td>

                <td class="px-6 py-4 text-right">

                    <button
                        onclick="testCDNAccount(${account.id})"
                        class="text-green-600 mr-4 hover:text-green-800"
                    >
                        测试
                    </button>

                    <button
                        onclick="editCDNAccount(${account.id})"
                        class="text-blue-600 mr-4 hover:text-blue-800"
                    >
                        编辑
                    </button>

                    <button
                        onclick="deleteCDNAccount(${account.id})"
                        class="text-red-600 hover:text-red-800"
                    >
                        删除
                    </button>

                </td>

            </tr>

        `)
        .join("");
}


// ============================================================
// 打开 Cloudflare Account 弹窗
// ============================================================

function openCDNAccountModal(account = null) {

    const modal = document.getElementById(
        "cdnAccountModal"
    );

    const title = document.getElementById(
        "cdnAccountModalTitle"
    );

    const idInput = document.getElementById(
        "cdnAccountId"
    );

    const nameInput = document.getElementById(
        "cdnAccountName"
    );

    const accountIdInput = document.getElementById(
        "cdnAccountAccountId"
    );

    const tokenInput = document.getElementById(
        "cfApiToken"
    );


    if (
        !modal ||
        !title ||
        !idInput ||
        !nameInput ||
        !accountIdInput ||
        !tokenInput
    ) {

        console.error(
            "Cloudflare 账号弹窗元素不存在"
        );

        return;
    }


    if (account) {

        title.textContent =
            "编辑 Cloudflare 账号";

        idInput.value =
            account.id;

        nameInput.value =
            account.name;

        accountIdInput.value =
            account.account_id;

        // Token 不回显
        tokenInput.value = "";

    } else {

        title.textContent =
            "添加 Cloudflare 账号";

        idInput.value =
            "";

        nameInput.value =
            "";

        accountIdInput.value =
            "";

        tokenInput.value =
            "";
    }


    modal.classList.remove("hidden");

    modal.classList.add("flex");
}


// ============================================================
// 关闭弹窗
// ============================================================

function closeCDNAccountModal() {

    const modal = document.getElementById(
        "cdnAccountModal"
    );

    if (!modal) {
        return;
    }

    modal.classList.add("hidden");

    modal.classList.remove("flex");
}


// ============================================================
// 编辑
// ============================================================

function editCDNAccount(id) {

    const account = cdnAccounts.find(
        item => item.id === id
    );


    if (!account) {

        alert("Cloudflare 账号不存在");

        return;
    }


    openCDNAccountModal(account);
}


// ============================================================
// 保存
// ============================================================

async function saveCDNAccount(event) {

    event.preventDefault();


    const id = document.getElementById(
        "cdnAccountId"
    ).value;


    const name = document.getElementById(
        "cdnAccountName"
    ).value
        .trim();


    const accountId = document.getElementById(
        "cdnAccountAccountId"
    ).value
        .trim();


    const apiToken = document.getElementById(
        "cfApiToken"
    ).value
        .trim();


    if (!name) {

        alert("请输入账号名称");

        return;
    }


    if (!accountId) {

        alert("请输入 Cloudflare Account ID");

        return;
    }


    // 新建必须有 Token
    if (!id && !apiToken) {

        alert("请输入 API Token");

        return;
    }


    const body = {
        name: name,
        account_id: accountId,
    };


    // 新建必须提交 Token
    // 编辑只有填写 Token 时才更新
    if (!id || apiToken) {

        body.api_token = apiToken;
    }


    try {

        await apiJson(
            id
                ? `/api/cdn-accounts/${id}`
                : "/api/cdn-accounts",

            {
                method: id
                    ? "PUT"
                    : "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify(body),
            }
        );


        closeCDNAccountModal();

        await loadCDNAccounts();


        alert(
            id
                ? "Cloudflare 账号修改成功"
                : "Cloudflare 账号添加成功"
        );


    } catch (error) {

        console.error(error);

        alert(
            error.message || "保存 Cloudflare 账号失败"
        );
    }
}


// ============================================================
// 测试 Cloudflare Token
// ============================================================

async function testCDNAccount(id) {

    try {

        const data = await apiJson(
            `/api/cdn-accounts/${id}/test`,
            {
                method: "POST",
            }
        );


        if (data) {

            alert(
                data.message ||
                "Cloudflare Token 正常"
            );
        }

    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            "Cloudflare Token 测试失败"
        );
    }
}


// ============================================================
// 删除
// ============================================================

async function deleteCDNAccount(id) {

    const account = cdnAccounts.find(
        item => item.id === id
    );


    if (!account) {

        alert("Cloudflare 账号不存在");

        return;
    }


    if (
        !confirm(
            `确定删除「${account.name}」吗？`
        )
    ) {
        return;
    }


    try {

        await apiJson(
            `/api/cdn-accounts/${id}`,
            {
                method: "DELETE",
            }
        );


        await loadCDNAccounts();


        alert("Cloudflare 账号删除成功");


    } catch (error) {

        console.error(error);

        alert(
            error.message ||
            "删除 Cloudflare 账号失败"
        );
    }
}


// ============================================================
// 表单提交
// ============================================================

const cdnAccountForm = document.getElementById(
    "cdnAccountForm"
);


if (cdnAccountForm) {

    cdnAccountForm.addEventListener(
        "submit",
        saveCDNAccount
    );
}


// ============================================================
// 页面初始化
// ============================================================

loadCDNAccounts();