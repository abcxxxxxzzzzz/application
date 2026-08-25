// ================================
// 批量添加域名
// ================================

window.batchCreateChecked = null;


// 打开批量添加
function openBatchCreateModal() {

    document.getElementById(
        "batchDomains"
    ).value = "";

    document.getElementById(
        "batchDomainCount"
    ).textContent = "0 个域名";

    document.getElementById(
        "batchCheckResult"
    ).innerHTML = "";

    document.getElementById(
        "batchCheckResult"
    ).classList.add("hidden");

    window.batchCreateChecked = null;

    document.getElementById(
        "batchPoolList"
    ).innerHTML = "";

    updateBatchJumpType();

    openModal("batchCreateModal");
}


// 解析域名
function parseDomains(text) {

    return [
        ...new Set(
            text
                .split(/[\n,\s]+/)
                .map(x =>
                    x
                        .trim()
                        .toLowerCase()
                        .replace(
                            /^https?:\/\//,
                            ""
                        )
                        .replace(
                            /\/.*$/,
                            ""
                        )
                        .replace(
                            /\.$/,
                            ""
                        )
                )
                .filter(Boolean)
        ),
    ];
}


// 域名数量
function updateBatchDomainCount() {

    const input =
        document.getElementById(
            "batchDomains"
        );

    if (!input) {
        return;
    }

    const count =
        parseDomains(input.value).length;

    document.getElementById(
        "batchDomainCount"
    ).textContent =
        `${count} 个域名`;
}


// 随机池
function addBatchPoolItem(
    target = "",
    weight = 1
) {

    const list =
        document.getElementById(
            "batchPoolList"
        );

    if (!list) {
        return;
    }

    const item =
        document.createElement("div");

    item.className =
        "batch-pool-item flex gap-2 items-center";

    item.innerHTML = `
        <input
            type="text"
            class="admin-input flex-1 batch-pool-target"
            placeholder="https://example.com"
            value="${escapeAttr(target)}">

        <input
            type="number"
            min="1"
            class="admin-input w-24 batch-pool-weight"
            value="${weight}"
            placeholder="权重">

        <button
            type="button"
            onclick="removeBatchPoolItem(this)"
            class="px-3 py-2
                   bg-red-500 hover:bg-red-600
                   text-white rounded-lg">
            删除
        </button>
    `;

    list.appendChild(item);

    updateBatchPoolEmpty();
}


// 删除随机池
function removeBatchPoolItem(button) {

    const item =
        button.closest(
            ".batch-pool-item"
        );

    if (item) {
        item.remove();
    }

    updateBatchPoolEmpty();
}


// 随机池空状态
function updateBatchPoolEmpty() {

    const list =
        document.getElementById(
            "batchPoolList"
        );

    const empty =
        document.getElementById(
            "batchPoolEmpty"
        );

    if (!list || !empty) {
        return;
    }

    const count =
        list.querySelectorAll(
            ".batch-pool-item"
        ).length;

    if (count === 0) {
        empty.classList.remove("hidden");
    } else {
        empty.classList.add("hidden");
    }
}


// 获取随机池
function getBatchPool() {

    const items = [];

    document
        .querySelectorAll(
            "#batchPoolList .batch-pool-item"
        )
        .forEach(item => {

            const target =
                item.querySelector(
                    ".batch-pool-target"
                ).value.trim();

            const weight =
                parseInt(
                    item.querySelector(
                        ".batch-pool-weight"
                    ).value,
                    10
                );

            if (!target) {
                return;
            }

            items.push({
                target_domain: target,
                weight: weight || 1,
                enabled: true,
            });
        });

    return items;
}


// 切换跳转类型
function updateBatchJumpType() {

    const jumpType =
        document.getElementById(
            "batchJumpType"
        ).value;

    const targetBox =
        document.getElementById(
            "batchTargetBox"
        );

    const poolBox =
        document.getElementById(
            "batchPoolBox"
        );

    if (!targetBox || !poolBox) {
        return;
    }

    if (jumpType === "random") {

        targetBox.classList.add("hidden");

        poolBox.classList.remove("hidden");

        const list =
            document.getElementById(
                "batchPoolList"
            );

        if (
            list &&
            !list.querySelector(
                ".batch-pool-item"
            )
        ) {
            addBatchPoolItem();
        }

    } else {

        targetBox.classList.remove("hidden");

        poolBox.classList.add("hidden");
    }
}


// 获取批量创建数据
function getBatchCreateData() {

    const domains =
        parseDomains(
            document.getElementById(
                "batchDomains"
            ).value
        );

    const jumpType =
        document.getElementById(
            "batchJumpType"
        ).value;

    const useGroupParams =
        document.getElementById(
            "batchUseGroupParams"
        ).checked;

    return {

        domains,

        group_id:
            Number(
                document.getElementById(
                    "batchGroupId"
                ).value
            ),

        jump_type: jumpType,

        jump_method:
            document.getElementById(
                "batchJumpMethod"
            ).value,

        status_code:
            Number(
                document.getElementById(
                    "batchStatusCode"
                ).value
            ),

        target_domain:
            jumpType === "random"
                ? null
                : document.getElementById(
                    "batchTargetDomain"
                ).value.trim() || null,

        embedded_code:
            document.getElementById(
                "batchEmbeddedCode"
            ).value.trim() || null,

        enabled:
            document.getElementById(
                "batchEnabled"
            ).checked,
            
        use_group_params: useGroupParams,

        pool:
            jumpType === "random"
                ? getBatchPool()
                : [],
    };
}


// ================================
// 检查批量添加
// ================================

async function checkBatchCreate() {

    const data =
        getBatchCreateData();

    if (!data.domains.length) {

        showToast(
            "请输入域名",
            false
        );

        return;
    }

    try {

        const result =
            await api(
                "/api/admin/domains/batch-create/check",
                {
                    method: "POST",
                    body: JSON.stringify(data),
                }
            );

        window.batchCreateChecked =
            result;

        renderBatchCheckResult(result);

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}


// ================================
// 渲染检查结果
// ================================

function renderBatchCheckResult(result) {

    const box =
        document.getElementById(
            "batchCheckResult"
        );

    if (!box) {
        return;
    }

    box.classList.remove("hidden");

    /*
     * 后端返回：
     *
     * {
     *   total: 3,
     *   items: [
     *     {
     *       domain: "a.com",
     *       can_create: true,
     *       reason: null
     *     },
     *     {
     *       domain: "b.com",
     *       can_create: false,
     *       reason: "域名已经存在"
     *     }
     *   ]
     * }
     */

    const items =
        result.items || [];

    const canCreateItems =
        items.filter(
            item => item.can_create
        );

    const cannotCreateItems =
        items.filter(
            item => !item.can_create
        );

    const total =
        result.total ??
        items.length;

    box.innerHTML = `

        <div class="bg-gray-50 rounded-lg p-4">

            <div class="grid grid-cols-3 gap-3 text-center">

                <div>
                    <div class="text-xl font-semibold">
                        ${total}
                    </div>

                    <div class="text-gray-500 text-sm">
                        总数
                    </div>
                </div>

                <div>
                    <div class="text-xl font-semibold text-green-600">
                        ${canCreateItems.length}
                    </div>

                    <div class="text-gray-500 text-sm">
                        可以添加
                    </div>
                </div>

                <div>
                    <div class="text-xl font-semibold text-red-600">
                        ${cannotCreateItems.length}
                    </div>

                    <div class="text-gray-500 text-sm">
                        无法添加
                    </div>
                </div>

            </div>

            ${
                cannotCreateItems.length
                    ? `
                    <div class="mt-4">

                        <div class="text-sm font-medium
                                    text-red-600 mb-2">

                            无法创建
                            ${cannotCreateItems.length}
                            个

                        </div>

                        <div
                            class="bg-white
                                   border border-red-200
                                   rounded-lg
                                   max-h-60
                                   overflow-y-auto">

                            ${
                                cannotCreateItems
                                    .map(
                                        item => `
                                        <div
                                            class="flex
                                                   items-center
                                                   justify-between
                                                   gap-4
                                                   px-3 py-2
                                                   border-b
                                                   last:border-b-0">

                                            <div
                                                class="text-sm
                                                       font-mono
                                                       break-all">

                                                ${escapeHtml(
                                                    item.domain
                                                )}

                                            </div>

                                            <div
                                                class="text-sm
                                                       text-red-500
                                                       shrink-0">

                                                ${escapeHtml(
                                                    item.reason ||
                                                    "无法创建"
                                                )}

                                            </div>

                                        </div>
                                        `
                                    )
                                    .join("")
                            }

                        </div>

                    </div>
                    `
                    : ""
            }

            ${
                canCreateItems.length
                    ? `
                    <button
                        type="button"
                        onclick="doBatchCreate()"
                        class="mt-4 w-full
                               px-4 py-2.5
                               bg-blue-600
                               hover:bg-blue-700
                               text-white
                               font-medium
                               rounded-lg
                               transition-colors">

                        确认添加
                        ${canCreateItems.length}
                        个

                    </button>
                    `
                    : `
                    <div
                        class="mt-4
                               text-center
                               text-gray-500
                               text-sm">

                        没有可以添加的域名

                    </div>
                    `
            }

        </div>
    `;
}


// ================================
// 真正批量创建
// ================================

async function doBatchCreate() {

    if (
        !window.batchCreateChecked
    ) {
        showToast(
            "请先检查域名",
            false
        );

        return;
    }

    const items =
        window.batchCreateChecked.items ||
        [];

    const canCreate =
        items
            .filter(
                item => item.can_create
            )
            .map(
                item => item.domain
            );

    if (!canCreate.length) {

        showToast(
            "没有可以添加的域名",
            false
        );

        return;
    }

    const data =
        getBatchCreateData();

    data.domains =
        canCreate;

    try {

        const result =
            await api(
                "/api/admin/domains/batch-create",
                {
                    method: "POST",
                    body: JSON.stringify(data),
                }
            );

        closeModal(
            "batchCreateModal"
        );

        window.batchCreateChecked =
            null;

        showToast(
            `成功添加 ${result.created} 个`
        );

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}


// ================================
// 监听
// ================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const input =
            document.getElementById(
                "batchDomains"
            );

        if (input) {

            input.addEventListener(
                "input",
                updateBatchDomainCount
            );
        }
    }
);




// =============================================== 批量添加+多域名 ================================
async function openBatchTargetCreateModal() {

    const modal =
        document.getElementById(
            "batchTargetCreateModal"
        );

    modal.classList.remove("hidden");

    document
        .getElementById(
            "batchTargetCreateInput"
        )
        ?.focus();
}


function closeBatchTargetCreateModal() {
    const modal = document.getElementById(
        "batchTargetCreateModal"
    );

    modal.classList.add("hidden");

    document.getElementById(
        "batchTargetCreateInput"
    ).value = "";

    const groupId =
        document.getElementById(
            "batchTargetCreateGroup"
        ).value = "";
    // document.getElementById(
    //     "batchTargetCreatePreview"
    // ).classList.add("hidden");
}


// 解析域名+域名
function parseBatchTargetCreateInput() {

    const input =
        document.getElementById(
            "batchTargetCreateInput"
        );

    const text =
        input.value.trim();

    const items = [];
    const errors = [];

    if (!text) {
        return {
            items,
            errors,
        };
    }

    const lines =
        text.split(/\r?\n/);

    lines.forEach(
        (rawLine, index) => {

            const lineNumber =
                index + 1;

            const line =
                rawLine.trim();

            if (!line) {
                return;
            }

            const match =
                line.match(
                    /^(\S+)\s+(.+)$/
                );

            if (!match) {

                errors.push(
                    `第 ${lineNumber} 行格式错误`
                );

                return;
            }

            const domain =
                match[1].trim();

            const target =
                match[2].trim();

            if (
                !/^https?:\/\//i.test(
                    target
                )
            ) {

                errors.push(
                    `第 ${lineNumber} 行目标地址必须以 http:// 或 https:// 开头`
                );

                return;
            }

            let jumpType = "direct";

            if (
                /^https?:\/\/\*\./i.test(
                    target
                )
            ) {

                jumpType = "wildcard";

            } else if (
                target.includes("*")
            ) {

                errors.push(
                    `第 ${lineNumber} 行泛域名地址格式错误`
                );

                return;
            }

            items.push({
                domain,
                target_domain: target,
                jump_type: jumpType,
            });

        }
    );

    return {
        items,
        errors,
    };
}


// 提交
async function submitBatchTargetCreate() {

    const {
        items,
        errors,
    } = parseBatchTargetCreateInput();

    if (errors.length) {

        showToast(
            errors
                .slice(0, 10)
                .join("<br>"),
            "error"
        );

        return;
    }

    if (!items.length) {

        showToast(
            "没有可添加的数据",
            "error"
        );

        return;
    }


    const groupId =
        document.getElementById(
            "batchTargetCreateGroup"
        ).value;

    if (!groupId) {
        showToast(
            "请选择分组",
            false
        );
        return;
    }

    const jumpMethod =
        document.getElementById(
            "batchTargetCreateMethod"
        ).value;


    const statusCode =
        Number(
            document.getElementById(
                "batchTargetCreateStatus"
            ).value
        );


    const enabled =
        document.getElementById(
            "batchTargetCreateEnabled"
        ).checked;


    const useGroupParams =
        document.getElementById(
            "batchTargetCreateUseGroupParams"
        ).checked;


    const embeddedCode =
        document.getElementById(
            "batchTargetCreateEmbeddedCode"
        ).value;


    try {

        const result =
            await api(
                "/api/admin/domains/batch-target-create",
                {
                    method: "POST",

                    body: JSON.stringify({

                        items,

                        group_id:
                            groupId
                                ? Number(groupId)
                                : null,

                        jump_method:
                            jumpMethod,

                        status_code:
                            statusCode,

                        enabled,

                        use_group_params:
                            useGroupParams,

                        embedded_code:
                            embeddedCode ||
                            null,

                    }),
                }
            );


        showToast(
            `成功添加 ${result.created} 条数据`,
        );


        closeBatchTargetCreateModal();

        await loadDomains();

    } catch (error) {

        console.error(
            "批量添加失败:",
            false
        );

        showToast(
            error.message ||
            "批量添加失败",
            false
        );

    }
}