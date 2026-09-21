// 加载域名列表
async function loadDomains() {

    showDomainLoading();

    const params =
        new URLSearchParams();

    params.set(
        "page",
        state.page
    );

    params.set(
        "page_size",
        state.pageSize
    );

    const search =
        document
            .getElementById(
                "searchInput"
            )
            .value
            .trim();

    const group =
        document
            .getElementById(
                "groupFilter"
            )
            .value;

    const type =
        document
            .getElementById(
                "typeFilter"
            )
            .value;

    const method =
        document
            .getElementById(
                "methodFilter"
            )
            .value;

    const enabled =
        document
            .getElementById(
                "enabledFilter"
            )
            .value;

    if (search)
        params.set(
            "search",
            search
        );

    if (group)
        params.set(
            "group_id",
            group
        );

    if (type)
        params.set(
            "jump_type",
            type
        );

    if (method)
        params.set(
            "jump_method",
            method
        );

    if (enabled)
        params.set(
            "enabled",
            enabled
        );

    try {

        const data =
            await api(
                "/api/admin/domains?" +
                params.toString()
            );

        state.domains = data.items;
        state.totalPages = data.pages;
        state.total = data.total;

        renderDomains();
        renderPageInfo();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    } finally {

        hideDomainLoading();

    }
}


// 非随机目标地址显示拼接后的最终地址。
function getDisplayTarget(item) {
    let target = item.target_domain || "";

    if (
        !item.use_group_params ||
        !item.group ||
        !item.group.custom_params
    ) {
        return target;
    }

    let params =
        item.group.custom_params.trim();

    if (!params) {
        return target;
    }

    // 去掉开头的 ? 或 &
    params = params.replace(/^[?&]+/, "");

    if (!params) {
        return target;
    }

    // 已经有查询参数
    if (target.includes("?")) {
        return `${target}&${params}`;
    }

    // 没有查询参数
    return `${target}?${params}`;
}

// 渲染域名
// 渲染域名
function renderDomains() {

    const tbody =
        document.getElementById(
            "domainTable"
        );

    tbody.innerHTML = "";

    const typeMap = {
        direct: "直接",
        wildcard: "泛域名",
        random: "随机",
    };

    const methodMap = {
        redirect: "重定向",
        js: "JS",
        html: "HTML",
        iframe: "Iframe"
    };

    for (
        const item of state.domains
    ) {

        const tr =
            document.createElement(
                "tr"
            );

        const group =
            state.groups.find(
                x =>
                    x.id ===
                    item.group_id
            );

        // ==========================
        // 最终展示目标地址
        // ==========================

        const displayTarget =
            getDisplayTarget({
                ...item,

                // 如果 /domains 已经返回 group，
                // 优先使用接口返回的 group
                group:
                    item.group ||
                    group ||
                    null,
            });

        // ==========================
        // 分组参数
        // ==========================

        const groupParams =
            item.group?.custom_params ||
            group?.custom_params ||
            "";

        tr.innerHTML = `

            <!-- 选择 -->

            <td class="table-td w-12 text-center align-middle">

                <div class="flex items-center justify-center">

                    <input
                        type="checkbox"
                        class="custom-checkbox domain-check"
                        value="${item.id}">

                </div>

            </td>


            <!-- ID -->

            <td class="table-td">

                ${item.id}

            </td>


            <!-- 域名 -->

            <td class="table-td font-medium">

                ${escapeHtml(
                    item.domain
                )}

            </td>


            <!-- 分组 -->

            <td class="table-td">

                ${escapeHtml(
                    group?.name ||
                    item.group?.name ||
                    "-"
                )}

            </td>


            <!-- 跳转类型 -->

            <td class="table-td">

                ${
                    item.jump_type === "direct"
                        ? `
                            <span
                                class="inline-flex items-center
                                       px-2.5 py-1
                                       rounded-full
                                       text-xs font-medium
                                       bg-blue-100
                                       text-blue-700">
                                直接
                            </span>
                          `
                        : item.jump_type === "wildcard"
                            ? `
                                <span
                                    class="inline-flex items-center
                                           px-2.5 py-1
                                           rounded-full
                                           text-xs font-medium
                                           bg-purple-100
                                           text-purple-700">
                                    泛域名
                                </span>
                              `
                            : item.jump_type === "random"
                                ? `
                                    <span
                                        class="inline-flex items-center
                                               px-2.5 py-1
                                               rounded-full
                                               text-xs font-medium
                                               bg-orange-100
                                               text-orange-700">
                                        随机
                                    </span>
                                  `
                                : escapeHtml(
                                    typeMap[
                                        item.jump_type
                                    ] ||
                                    item.jump_type
                                )
                }

            </td>


            <!-- 跳转方式 -->

            <td class="table-td">

                ${
                    methodMap[
                        item.jump_method
                    ] ||
                    item.jump_method
                }

            </td>


            <!-- 状态码 -->

            <td class="table-td">

                ${item.status_code}

            </td>


            <!-- 目标地址 -->

            <td class="table-td max-w-[650px]">

                ${
                    item.jump_type === "random"

                        ? (

                            item.pool &&
                            item.pool.length

                                ? `

                                    <div
                                        class="space-y-1
                                               max-w-[650px]">

                                        ${item.pool
                                            .map(
                                                pool => `

                                                    <div
                                                        class="url-tooltip-trigger
                                                               truncate
                                                               max-w-[650px]
                                                               cursor-help"
                                                        data-tooltip="${escapeHtml(
                                                            pool.target_domain
                                                        )}"
                                                    >

                                                        ${escapeHtml(
                                                            pool.target_domain
                                                        )}

                                                        <span
                                                            class="text-gray-400 ml-1">

                                                            × ${pool.weight}

                                                        </span>

                                                    </div>

                                                `
                                            )
                                            .join("")}

                                    </div>

                                  `

                                : `

                                    <span
                                        class="text-gray-400">

                                        暂无跳转域名

                                    </span>

                                  `

                        )

                        : (

                            displayTarget

                                ? `

                                    <div
                                        class="url-tooltip-trigger
                                               truncate
                                               max-w-[650px]
                                               cursor-help"
                                        data-tooltip="${escapeHtml(
                                            displayTarget
                                        )}"
                                    >

                                        ${escapeHtml(
                                            displayTarget
                                        )}

                                    </div>

                                  `

                                : `

                                    <span
                                        class="text-gray-400">

                                        -

                                    </span>

                                  `

                        )

                }

            </td>


            <!-- 分组参数 -->
            <td class="table-td max-w-[250px]">

                ${
                    item.use_group_params
                        ? (
                            groupParams
                                ? `
                                    <div
                                        class="truncate
                                              max-w-[220px]
                                              cursor-help
                                              text-green-600"
                                        data-tooltip="${escapeHtml(
                                            groupParams
                                        )}"
                                    >
                                        已启用：
                                        ${escapeHtml(
                                            groupParams
                                        )}
                                    </div>
                                  `
                                : `
                                    <span
                                        class="text-yellow-600"
                                        title="已开启分组 URL 参数，但当前分组没有配置参数">
                                        已启用：未配置参数
                                    </span>
                                  `
                        )
                        : `
                            <span class="text-gray-400">
                                未启用
                            </span>
                          `
                }

            </td>


            <!-- 启用状态 -->

            <td class="table-td">

                ${
                    item.enabled

                        ? `

                            <span class="status-on">

                                启用

                            </span>

                          `

                        : `

                            <span class="status-off">

                                禁用

                            </span>

                          `

                }

            </td>


            <!-- 操作 -->

            <td class="table-td text-right">

                <button
                    type="button"
                    onclick="editDomain(${item.id})"
                    class="text-blue-600 mr-3">

                    编辑

                </button>

                <button
                    type="button"
                    onclick="deleteDomain(${item.id})"
                    class="text-red-600">

                    删除

                </button>

            </td>

        `;

        tbody.appendChild(tr);
    }


    // ==========================
    // 全选状态
    // ==========================

    const selectAll =
        document.getElementById(
            "selectAll"
        );

    if (selectAll) {

        selectAll.checked =
            false;

    }
}