// 批量启用、禁用、移动、删除。

function toggleSelectAll(
    checked
) {
    document
        .querySelectorAll(
            ".domain-check"
        )
        .forEach(
            el => {
                el.checked =
                    checked;
            }
        );
}


// 批量启用|禁用
async function batchEnabled(
    enabled
) {

    const ids =
        getSelectedIds();

    if (!ids.length) {
        showToast(
            "请先选择域名",
            false
        );
        return;
    }

    try {

        const data =
            await api(
                "/api/admin/domains/batch-enabled",
                {
                    method: "POST",
                    body:
                        JSON.stringify({
                            ids,
                            enabled,
                        }),
                }
            );

        showToast(
            `已更新 ${data.updated} 个域名`
        );

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}


// 批量修改分组
function openBatchGroupModal() {

    const ids =
        getSelectedIds();

    if (!ids.length) {
        showToast(
            "请先选择域名",
            false
        );
        return;
    }

    openModal(
        "batchGroupModal"
    );
}


async function batchGroup() {

    const ids =
        getSelectedIds();

    if (!ids.length) {
        showToast(
            "请先选择域名",
            false
        );
        return;
    }

    const groupId =
        Number(
            document.getElementById(
                "batchMoveGroupId"
            ).value
        );

    if (!groupId) {
        showToast(
            "请选择分组",
            false
        );
        return;
    }

    try {

        const data =
            await api(
                "/api/admin/domains/batch-group",
                {
                    method: "POST",
                    body:
                        JSON.stringify({
                            ids,
                            group_id:
                                groupId,
                        }),
                }
            );

        closeModal(
            "batchGroupModal"
        );

        showToast(
            `已更新 ${data.updated} 个域名`
        );

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}


// 批量删除
async function batchDelete() {

    const ids =
        getSelectedIds();

    if (!ids.length) {
        showToast(
            "请先选择域名",
            false
        );
        return;
    }

    if (
        !confirm(
            `确定删除 ${ids.length} 个域名吗？`
        )
    ) {
        return;
    }

    try {

        const data =
            await api(
                "/api/admin/domains/batch-delete",
                {
                    method: "POST",
                    body:
                        JSON.stringify({
                            ids,
                        }),
                }
            );

        showToast(
            `已删除 ${data.deleted} 个域名`
        );

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}



// ==============================
// 批量搜索
// ==============================

function openBatchSearchModal() {
    const input = document.getElementById(
        "batchSearchDomains"
    );

    const result = document.getElementById(
        "batchSearchResult"
    );

    if (input) {
        input.value = "";
    }

    if (result) {
        result.innerHTML = "";
        result.classList.add("hidden");
    }

    openModal("batchSearchModal");
}


function parseDomains(text) {

    return [
        ...new Set(
            String(text || "")
                .split(/[\n,\s]+/)
                .map(x => {
                    return x
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
                        );
                })
                .filter(Boolean)
        )
    ];
}


async function batchSearch() {

    const input =
        document.getElementById(
            "batchSearchDomains"
        );

    const domains =
        parseDomains(
            input ? input.value : ""
        );

    if (!domains.length) {
        showToast(
            "请输入域名",
            false
        );
        return;
    }

    try {

        const data = await api(
            "/api/admin/domains/search-batch",
            {
                method: "POST",
                body: JSON.stringify({
                    domains
                })
            }
        );

        /*
         * 直接把批量搜索结果
         * 放进现有域名表格
         */
        state.domains =
            data.items || [];

        /*
         * 批量搜索没有分页
         */
        state.page = 1;
        state.totalPages = 1;

        /*
         * 使用现有表格渲染
         */
        renderDomains();

        renderPageInfo();

        /*
         * 关闭弹窗
         */
        closeModal(
            "batchSearchModal"
        );

        /*
         * 提示搜索结果
         */
        const found =
            data.found || 0;

        const notFound =
            data.not_found
                ? data.not_found.length
                : 0;

        if (!found) {

            showToast(
                `没有找到域名`,
                false
            );

        } else if (notFound) {

            showToast(
                `找到 ${found} 个，${notFound} 个不存在`
            );

        } else {

            showToast(
                `找到 ${found} 个域名`
            );
        }

    } catch (error) {

        showToast(
            error.message || "批量搜索失败",
            false
        );
    }
}




// ==============================
// 批量修改目标域名
// ==============================
function openBatchReplaceTargetDomainModal() {

    const selectedIds =
        getSelectedIds();

    if (!selectedIds.length) {

        showToast(
            "请先选择要处理的域名",
            false
        );

        return;
    }

    const modal =
        document.getElementById(
            "batchReplaceTargetDomainModal"
        );

    if (!modal) {
        console.error(
            "找不到 batchReplaceTargetDomainModal"
        );
        return;
    }

    modal.classList.remove("hidden");

    document.getElementById(
        "batchReplaceOldDomain"
    ).value = "";

    document.getElementById(
        "batchReplaceNewDomain"
    ).value = "";

    const preview =
        document.getElementById(
            "batchReplaceTargetDomainPreview"
        );

    if (preview) {
        preview.classList.add("hidden");
        preview.textContent = "";
    }

    document.getElementById(
        "batchReplaceOldDomain"
    )?.focus();
}


function closeBatchReplaceTargetDomainModal() {

    const modal =
        document.getElementById(
            "batchReplaceTargetDomainModal"
        );

    if (modal) {
        modal.classList.add("hidden");
    }
}



function previewBatchReplaceTargetDomain() {

    const oldDomain =
        document.getElementById(
            "batchReplaceOldDomain"
        ).value.trim().toLowerCase();

    const newDomain =
        document.getElementById(
            "batchReplaceNewDomain"
        ).value.trim().toLowerCase();

    if (!oldDomain) {

        showToast(
            "请输入原顶级域名",
            "error"
        );

        return;
    }

    if (!newDomain) {

        showToast(
            "请输入新顶级域名",
            "error"
        );

        return;
    }

    if (oldDomain === newDomain) {

        showToast(
            "原域名和新域名不能相同",
            "error"
        );

        return;
    }

    const selectedIds =
        getSelectedIds();

    let count = 0;

    selectedIds.forEach(id => {

        const item =
            state.domains.find(
                x => x.id === id
            );

        if (!item) {
            return;
        }

        if (
            item.target_domain &&
            targetDomainMatches(
                item.target_domain,
                oldDomain
            )
        ) {
            count++;
        }

        if (
            item.pool &&
            item.pool.length
        ) {

            item.pool.forEach(pool => {

                if (
                    pool.target_domain &&
                    targetDomainMatches(
                        pool.target_domain,
                        oldDomain
                    )
                ) {
                    count++;
                }

            });

        }

    });

    const preview =
        document.getElementById(
            "batchReplaceTargetDomainPreview"
        );

    if (!preview) {
        return;
    }

    preview.classList.remove("hidden");

    preview.textContent =
        `预计修改 ${count} 个目标地址：` +
        `${oldDomain} → ${newDomain}`;
}


function targetDomainMatches(
    target,
    oldDomain
) {
    if (!target || !oldDomain) {
        return false;
    }

    let value = target.trim();

    // 去掉协议
    value = value.replace(
        /^https?:\/\//i,
        ""
    );

    // 去掉路径、参数、fragment
    value = value.split(
        /[/?#]/
    )[0];

    // 去掉通配符
    value = value.replace(
        /^\*\./,
        ""
    );

    return (
        value.toLowerCase() ===
        oldDomain
            .trim()
            .replace(/^\*\./, "")
            .toLowerCase()
    );
}



async function submitBatchReplaceTargetDomain() {

    const oldDomain =
        document.getElementById(
            "batchReplaceOldDomain"
        ).value.trim().toLowerCase();

    const newDomain =
        document.getElementById(
            "batchReplaceNewDomain"
        ).value.trim().toLowerCase();

    if (!oldDomain) {

        showToast(
            "请输入原顶级域名",
            false
        );

        return;
    }

    if (!newDomain) {

        showToast(
            "请输入新顶级域名",
            false
        );

        return;
    }

    const selectedIds =
        getSelectedIds();

    if (!selectedIds.length) {

        showToast(
            "请选择需要处理的域名",
            false
        );

        return;
    }

    if (
        !confirm(
            `确定将选中的 ${selectedIds.length} 个域名目标地址中的\n\n` +
            `${oldDomain} → ${newDomain}\n\n` +
            `进行替换吗？`
        )
    ) {
        return;
    }

    try {

        const result =
            await api(
                "/api/admin/domains/batch-replace-target-domain",
                {
                    method: "POST",

                    body: JSON.stringify({
                        domain_ids:
                            selectedIds,

                        old_domain:
                            oldDomain,

                        new_domain:
                            newDomain,
                    }),
                }
            );

        showToast(
            `替换完成，共修改 ${result.updated_targets} 个目标地址`,
        );

        closeBatchReplaceTargetDomainModal();

        await loadDomains();

    } catch (error) {

        console.error(
            "批量替换目标域名失败:",
            error
        );

        showToast(
            error.message ||
            "批量替换目标域名失败",
            false
        );
    }
}




// ==============================
// 批量启用|禁用分组参数
// ==============================
async function batchUpdateGroupParams(enabled) {

    const selectedIds =
        getSelectedIds();

    if (!selectedIds.length) {

        showToast(
            "请先选择要处理的域名",
            false
        );

        return;
    }

    const action =
        enabled
            ? "启用"
            : "禁用";

    if (
        !confirm(
            `确定要${action}选中的 ${selectedIds.length} 个域名的分组参数吗？`
        )
    ) {
        return;
    }

    try {

        const result =
            await api(
                "/api/admin/domains/batch-group-params",
                {
                    method: "POST",

                    body: JSON.stringify({
                        domain_ids:
                            selectedIds,

                        use_group_params:
                            enabled,
                    }),
                }
            );

        showToast(
            `${action}成功，共处理 ${result.updated} 个域名`,
            "success"
        );

        await loadDomains();

    } catch (error) {

        console.error(
            "批量修改分组参数失败:",
            error
        );

        showToast(
            error.message ||
            `批量${action}分组参数失败`,
            false
        );
    }
}



// ==============================
// 批量清除所有域名 Redis 缓存
// ==============================
async function clearAllDomainCache() {

    if (
        !confirm(
            "确定要清除所有域名的 Redis 缓存吗？"
        )
    ) {
        return;
    }

    try {

        const result = await api(
            "/api/admin/domains/cache/all",
            {
                method: "DELETE",
            }
        );

        showToast(
            result.message ||
            "所有域名缓存已清除",
        );

    } catch (error) {

        console.error(
            "清除全部缓存失败:",
            error
        );

        showToast(
            error.message ||
            "清除全部缓存失败",
            false
        );
    }
}