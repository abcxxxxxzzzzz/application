let groups = [];
let cdnAccounts = [];
let domains = [];

let currentTargetDomainId = null;


// ============================================================
// 初始化
// ============================================================

async function initDomainsPage() {
    try {
        await Promise.all([
            loadGroups(),
            loadCDNAccounts(),
        ]);

        await loadDomains();

    } catch (error) {
        console.error(error);
        alert(error.message || "页面加载失败");
    }
}


// ============================================================
// Group
// ============================================================

async function loadGroups() {
    const data = await apiJson("/api/groups");

    if (!data) {
        return;
    }

    groups = data;

    renderGroupOptions();
}


function renderGroupOptions() {
    const select = document.getElementById("domainGroupId");

    if (!select) {
        return;
    }

    if (!groups.length) {
        select.innerHTML = `
            <option value="">
                暂无分组
            </option>
        `;

        return;
    }

    select.innerHTML = groups
        .map(group => `
            <option value="${group.id}">
                ${escapeHtml(group.name)}
            </option>
        `)
        .join("");
}


// ============================================================
// Cloudflare Account
// ============================================================

async function loadCDNAccounts() {
    const data = await apiJson("/api/cdn-accounts");

    if (!data) {
        return;
    }

    cdnAccounts = data;

    renderCDNAccountOptions();
}


function renderCDNAccountOptions() {
    const select = document.getElementById(
        "domainCDNAccountId"
    );

    if (!select) {
        return;
    }

    if (!cdnAccounts.length) {
        select.innerHTML = `
            <option value="">
                暂无 Cloudflare 账号
            </option>
        `;

        return;
    }

    select.innerHTML = cdnAccounts
        .map(account => `
            <option value="${account.id}">
                ${escapeHtml(account.name)}
                (${escapeHtml(account.account_id)})
            </option>
        `)
        .join("");
}


// ============================================================
// Domain 加载关联 CDN
// ============================================================
async function loadDomainCDNOptions(domainId) {
    const targets = await apiJson(
        `/api/domains/${domainId}/cdn-targets`
    );

    return [
        ...targets,
    ];
}

function renderDomainCDNOptions(targets, currentCDN, selectId = "domainDesiredCDN") {
    const select = document.getElementById(selectId);

    if (!select) { console.error("找不到 #domainDesiredCDN"); return; }


    select.innerHTML = targets.map(item => `
        <option
            value="${escapeHtml(item.cdn)}"
            ${item.cdn === currentCDN ? "selected" : ""}
        >
            ${escapeHtml(item.cdn)}
            (${escapeHtml(item.cname)})
            ${item.proxied === 1 ? "(CF代理)" : "(仅DNS解析)"}
        </option>
    `).join("");
}

// ============================================================
// Domain
// ============================================================


async function loadDomains() {
    const allDomains = [];

    for (const group of groups) {
        const data = await apiJson(
            `/api/groups/${group.id}/domains`
        );

        if (!data) {
            return;
        }

        for (const domain of data) {
            allDomains.push({
                ...domain,
                group_name: group.name,
            });
        }
    }

    domains = allDomains;

    renderDomains();
}


function renderDomains() {
    const tbody = document.getElementById(
        "domainsTableBody"
    );

    if (!tbody) {
        return;
    }

    if (!domains.length) {
        tbody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="px-5 py-10 text-center text-gray-400"
                >
                    暂无域名
                </td>
            </tr>
        `;

        return;
    }

    tbody.innerHTML = domains
        .map(domain => {

            const enabledClass = domain.enabled
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-500";

            const enabledText = domain.enabled
                ? "启用"
                : "停用";

            const cdnName = getCDNName(
                domain.desired_cdn
            );

            const account = cdnAccounts.find(
                item => item.id === domain.cdn_account_id
            );

            const accountName = account
                ? account.name
                : `ID: ${domain.cdn_account_id}`;

            return `
                <tr class="border-b hover:bg-gray-50">

                    <td class="px-5 py-4 font-medium">
                        ${escapeHtml(domain.domain)}
                    </td>

                    <td class="px-5 py-4">
                        ${escapeHtml(domain.group_name || "-")}
                    </td>

                    <td class="px-5 py-4 text-sm">
                        ${escapeHtml(accountName)}
                    </td>

                    <td class="px-5 py-4">

                        <span
                            class="px-2 py-1 rounded text-xs bg-blue-100 text-blue-700"
                        >
                            ${cdnName?.trim() ? escapeHtml(cdnName) : "未手动关联CDN"}
                        </span>

                    </td>

                    <td class="px-5 py-4">

                        <span
                            class="px-2 py-1 rounded text-xs ${enabledClass}"
                        >
                            ${enabledText}
                        </span>

                    </td>

                    <td
                        class="px-5 py-4 text-sm text-gray-500 max-w-xs truncate"
                        title="${escapeHtml(domain.switch_remark || "")}"
                    >
                        ${escapeHtml(domain.switch_remark || "-")}
                    </td>

                    <td class="px-5 py-4">

                        <div class="flex justify-end gap-2">

                            <button
                                onclick="openSwitchModal(${domain.id})"
                                class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                                CDN 切换
                            </button>

                            <button
                                onclick="openCDNTargetModal(${domain.id})"
                                class="px-3 py-1.5 text-sm border rounded hover:bg-gray-100"
                            >
                                CDN|CNAME 配置
                            </button>


                            <button
                                onclick="deleteDomain(${domain.id})"
                                class="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50"
                            >
                                删除
                            </button>

                        </div>

                    </td>

                </tr>
            `;
        })
        .join("");
}


function getCDNName(cdn) {
    const names = {
        cf: "Cloudflare",
        aws: "AWS",
        aliyun: "阿里云",
    };

    return names[cdn] || cdn;
}


// ============================================================
// Domain Modal
// ============================================================

function openDomainModal() {
    document.getElementById(
        "domainModalTitle"
    ).textContent = "添加域名";

    document.getElementById(
        "domainId"
    ).value = "";

    document.getElementById(
        "domainGroupId"
    ).disabled = false;

    document.getElementById(
        "domainCDNAccountId"
    ).disabled = false;

    document.getElementById(
        "domainName"
    ).value = "";

    // document.getElementById(
    //     "domainDesiredCDN"
    // ).value = "";

    document.getElementById(
        "domainEnabled"
    ).checked = true;

    document.getElementById(
        "domainModal"
    ).classList.remove("hidden");

    document.getElementById(
        "domainModal"
    ).classList.add("flex");
}


function closeDomainModal() {
    document.getElementById(
        "domainModal"
    ).classList.add("hidden");

    document.getElementById(
        "domainModal"
    ).classList.remove("flex");
}


// async function editDomain(id) {
//     const domain = domains.find(item => item.id === id);

//     if (!domain) {
//         alert("域名不存在");
//         return;
//     }

//     const cdnOptions = await loadDomainCDNOptions(domain.id);


//     document.getElementById(
//         "domainModalTitle"
//     ).textContent = "编辑域名";

//     document.getElementById(
//         "domainId"
//     ).value = domain.id;

//     document.getElementById(
//         "domainGroupId"
//     ).value = domain.group_id;

//     // 编辑时禁止修改 Group
//     document.getElementById(
//         "domainGroupId"
//     ).disabled = true;

//     document.getElementById(
//         "domainCDNAccountId"
//     ).disabled = false;

//     document.getElementById(
//         "domainCDNAccountId"
//     ).value = domain.cdn_account_id;

//     document.getElementById(
//         "domainName"
//     ).value = domain.domain;

//     // document.getElementById(
//     //     "domainDesiredCDN"
//     // ).value = domain.desired_cdn;



//     document.getElementById(
//         "domainEnabled"
//     ).checked = domain.enabled;

//     document.getElementById(
//         "domainModal"
//     ).classList.remove("hidden");

//     document.getElementById(
//         "domainModal"
//     ).classList.add("flex");

//     renderDomainCDNOptions(
//         cdnOptions,
//         domain.desired_cdn
//     );
// }


// ============================================================
// Domain Create / Update
// ============================================================

document.getElementById(
    "domainForm"
).addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const id = document.getElementById(
            "domainId"
        ).value;

        const domainName = document.getElementById(
            "domainName"
        ).value
            .trim()
            .toLowerCase()
            .replace(/\.$/, "");

        const cdnAccountId = Number(
            document.getElementById(
                "domainCDNAccountId"
            ).value
        );

        // const desiredCDN = document.getElementById(
        //     "domainDesiredCDN"
        // ).value;

        const enabled = document.getElementById(
            "domainEnabled"
        ).checked;


        if (!domainName) {
            alert("请输入域名");
            return;
        }

        if (!cdnAccountId) {
            alert("请选择 Cloudflare 账号");
            return;
        }


        const data = {
            domain: domainName,
            cdn_account_id: cdnAccountId,
            enabled: enabled,
        };


        try {

            if (id) {

                await apiJson(
                    `/api/domains/${id}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },

                        body: JSON.stringify(data),
                    }
                );

            } else {

                const groupId = document.getElementById(
                    "domainGroupId"
                ).value;

                if (!groupId) {
                    alert("请选择分组");
                    return;
                }


                await apiJson(
                    `/api/groups/${groupId}/domains`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },

                        body: JSON.stringify(data),
                    }
                );
            }


            closeDomainModal();

            await loadDomains();

            alert(
                id
                    ? "域名修改成功"
                    : "域名添加成功"
            );


        } catch (error) {

            console.error(error);

            alert(
                error.message || "保存失败"
            );
        }
    }
);


// ============================================================
// Delete Domain
// ============================================================

async function deleteDomain(id) {
    const domain = domains.find(
        item => item.id === id
    );

    if (!domain) {
        alert("域名不存在");
        return;
    }


    if (
        !confirm(
            `确定删除域名 ${domain.domain} 吗？`
        )
    ) {
        return;
    }


    try {

        await apiJson(
            `/api/domains/${id}`,
            {
                method: "DELETE",
            }
        );


        await loadDomains();

        alert("删除成功");


    } catch (error) {

        console.error(error);

        alert(
            error.message || "删除失败"
        );
    }
}


// ============================================================
// CDN Target Modal
// ============================================================

async function openCDNTargetModal(domainId) {
    const domain = domains.find(
        item => item.id === domainId
    );

    if (!domain) {
        alert("域名不存在");
        return;
    }


    currentTargetDomainId = domainId;


    document.getElementById(
        "cdnTargetDomain"
    ).textContent = domain.domain;


    document.getElementById(
        "targetCDN"
    ).value = "";


    document.getElementById(
        "targetCNAME"
    ).value = "";

    document.getElementById("targetProxied").checked = false;
    


    document.getElementById(
        "cdnTargetModal"
    ).classList.remove("hidden");

    document.getElementById(
        "cdnTargetModal"
    ).classList.add("flex");


    try {

        await loadCDNTargets();

    } catch (error) {

        console.error(error);

        alert(
            error.message || "加载 CDN 配置失败"
        );
    }
}


function closeCDNTargetModal() {
    document.getElementById(
        "cdnTargetModal"
    ).classList.add("hidden");

    document.getElementById(
        "cdnTargetModal"
    ).classList.remove("flex");

    currentTargetDomainId = null;
}


// ============================================================
// CDN Targets
// ============================================================

async function loadCDNTargets() {
    if (!currentTargetDomainId) {
        return;
    }


    const targets = await apiJson(
        `/api/domains/${currentTargetDomainId}/cdn-targets`
    );


    if (!targets) {
        return;
    }


    const tbody = document.getElementById(
        "cdnTargetsTableBody"
    );


    if (!targets.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="3"
                    class="px-4 py-8 text-center text-gray-400"
                >
                    暂无 CDN CNAME
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = targets
        .map(target => `
            <tr class="border-b">

                <td class="px-4 py-3">
                    <span
                        class="px-2 py-1 rounded bg-gray-100 text-sm"
                    >
                        ${escapeHtml(target.cdn)}
                    </span>
                </td>

                <td class="px-4 py-3 break-all">
                    ${escapeHtml(target.cname)}
                </td>


                <!-- CF Proxy -->
                <td class="px-4 py-3">
                    <label class="inline-flex items-center cursor-pointer">
                        <input
                            type="checkbox"
                            class="sr-only peer"
                            ${target.proxied === 1 ? "checked" : ""}
                            disabled
                        >

                        <div class="
                            relative w-10 h-5
                            bg-gray-300
                            rounded-full
                            peer-checked:bg-green-500
                            after:content-['']
                            after:absolute
                            after:top-[2px]
                            after:left-[2px]
                            after:w-4
                            after:h-4
                            after:bg-white
                            after:rounded-full
                            after:transition-all
                            peer-checked:after:translate-x-5
                        "></div>

                        <span class="ml-2 text-sm text-gray-600">
                             ${target.proxied === 1 ? "启用" : "禁用"}
                        </span>
                    </label>
                </td>


                <td class="px-4 py-3 text-right">

                    <button
                        onclick="deleteCDNTarget(${target.id})"
                        class="text-red-600 text-sm hover:text-red-800"
                    >
                        删除
                    </button>

                </td>

            </tr>
        `)
        .join("");
}


// // CF PROXY 切换开关
// async function toggleCDNTargetProxy(targetId, proxied) {
//     try {
//         await apiJson(
//             `/api/domains/${currentTargetDomainId}/cdn-targets/${targetId}`,
//             {
//                 method: "PUT",
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//                 body: JSON.stringify({
//                     proxied: proxied,
//                 }),
//             }
//         );

//         await loadCDNTargets();

//     } catch (error) {
//         console.error(error);
//         alert(error.message || "修改 CF 代理状态失败");

//         // 保存失败，重新加载恢复原状态
//         await loadCDNTargets();
//     }
// }

// ============================================================
// Add CDN Target
// ============================================================

async function addCDNTarget() {
    if (!currentTargetDomainId) {
        alert("没有选择域名");
        return;
    }


    const cdnInput = document.getElementById(
        "targetCDN"
    );

    const cnameInput = document.getElementById(
        "targetCNAME"
    );




    // const proxied = document.getElementById("targetProxied").checked;
    const proxied = document.getElementById("targetProxied").checked ? 1 : 0;

    
    const cdn = cdnInput.value
        .trim()
        .toLowerCase();


    const cname = cnameInput.value
        .trim()
        .toLowerCase()
        .replace(/\.$/, "");


    if (!cdn) {
        alert("请输入 CDN");
        cdnInput.focus();
        return;
    }


    if (!cname) {
        alert("请输入 CNAME");
        cnameInput.focus();
        return;
    }




    try {

        await apiJson(
            `/api/domains/${currentTargetDomainId}/cdn-targets`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    cdn,
                    cname,
                    proxied
                }),
            }
        );

        // 清空输入
        cdnInput.value = "";
        cnameInput.value = "";

        // 重置 CF Proxy 开关
        document.getElementById("targetProxied").checked = false;

        await loadCDNTargets();


    } catch (error) {

        console.error(error);

        alert(
            error.message || "添加 CDN CNAME 失败"
        );
    }
}


// ============================================================
// Delete CDN Target
// ============================================================

async function deleteCDNTarget(targetId) {

    if (!currentTargetDomainId) {
        return;
    }


    if (
        !confirm(
            "确定删除这个 CDN CNAME 吗？"
        )
    ) {
        return;
    }


    try {

        await apiJson(
            `/api/domains/${currentTargetDomainId}/cdn-targets/${targetId}`,
            {
                method: "DELETE",
            }
        );


        await loadCDNTargets();


    } catch (error) {

        console.error(error);

        alert(
            error.message || "删除 CDN CNAME 失败"
        );
    }
}


// ============================================================
// CDN Switch Modal
// ============================================================

async function openSwitchModal(domainId) {

    const domain = domains.find(item => item.id === domainId);

    if (!domain) {
        alert("域名不存在");
        return;
    }


    const cdnOptions = await loadDomainCDNOptions(domain.id);


    document.getElementById(
        "switchDomainId"
    ).value = domain.id;


    document.getElementById(
        "switchDomainName"
    ).textContent = domain.domain;


    // document.getElementById(
    //     "switchCDN"
    // ).value = domain.desired_cdn;


    document.getElementById(
        "switchRemark"
    ).value = "";


    document.getElementById(
        "switchModal"
    ).classList.remove("hidden");

    document.getElementById(
        "switchModal"
    ).classList.add("flex");

    renderDomainCDNOptions(
        cdnOptions,
        domain.desired_cdn,
        "switchCDN"
    );
}


function closeSwitchModal() {

    document.getElementById(
        "switchModal"
    ).classList.add("hidden");

    document.getElementById(
        "switchModal"
    ).classList.remove("flex");
}


// ============================================================
// CDN Switch
// ============================================================

async function confirmSwitch() {

    const domainId = document.getElementById(
        "switchDomainId"
    ).value;


    const cdn = document.getElementById(
        "switchCDN"
    ).value;


    const remark = document.getElementById(
        "switchRemark"
    ).value.trim();


    if (!domainId) {
        alert("域名 ID 不存在");
        return;
    }


    if (!cdn) {
        alert("请选择 CDN");
        return;
    }


    const domain = domains.find(
        item => String(item.id) === String(domainId)
    );


    if (!domain) {
        alert("域名不存在");
        return;
    }


    if (!domain.enabled) {
        alert("该域名已停用，不能切换");
        return;
    }


    const cdnName = getCDNName(cdn);


    if (
        !confirm(
            `确定将 ${domain.domain} 切换到 ${cdnName} 吗？`
        )
    ) {
        return;
    }


    try {

        const result = await apiJson(
            `/api/domains/${domainId}/switch`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    cdn,
                    remark: remark || null,
                }),
            }
        );


        if (!result) {
            return;
        }


        closeSwitchModal();


        await loadDomains();


        alert(
            `切换到 ${cdnName} 成功`
        );


    } catch (error) {

        console.error(error);

        alert(
            `切换失败：${error.message || "未知错误"}`
        );
    }
}


// ============================================================
// 页面初始化
// ============================================================

initDomainsPage();