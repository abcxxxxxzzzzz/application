// 把分组管理全部放这里

async function loadGroups() {
    const data =
        await api(
            "/api/admin/groups"
        );

    state.groups =
        data.items || data;

    const selects = [
        "groupFilter",
        "groupId",
        "batchGroupId",
        "batchMoveGroupId",
        "batch-group-select",
        "batchTargetCreateGroup"
    ];

    for (const id of selects) {

        const el =
            document.getElementById(id);

        if (!el) continue;

        const first =
            el.options[0];

        el.innerHTML = "";

        if (first) {
            el.appendChild(first);
        }

        for (const group of state.groups) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                group.id;

            option.textContent =
                group.name;

            el.appendChild(option);
        }
    }

    renderGroups();
}


// // 分组列表
function renderGroups() {
    const container =
        document.getElementById(
            "groups-container"
        );

    if (!container) return;

    if (!state.groups.length) {

        container.innerHTML = `
            <div class="text-gray-500
                        py-8
                        text-center">
                暂无分组
            </div>
        `;

        return;
    }

    container.innerHTML =
        state.groups
            .map(
                group => `
                    <div
                        class="flex
                               items-center
                               justify-between
                               border
                               rounded-lg
                               p-4
                               mb-2
                               bg-white">

                        <div>

                            <div class="font-medium">
                                ${escapeHtml(
                                    group.name
                                )}
                            </div>

                            <div
                                class="text-sm
                                       text-gray-500">

                                ${group.domain_count || 0}
                                个域名

                            </div>

                        </div>

                        <div class="flex gap-2">

                            <button
                                type="button"
                                onclick="openGroupEditModal(${group.id})"
                                class="px-3 py-1.5
                                       rounded
                                       bg-gray-100
                                       hover:bg-gray-200">

                                修改

                            </button>

                            <button
                                type="button"
                                onclick="deleteGroup(${group.id})"
                                class="px-3 py-1.5
                                       rounded
                                       bg-red-50
                                       text-red-600
                                       hover:bg-red-100">

                                删除

                            </button>

                        </div>

                    </div>
                `
            )
            .join("");
}


// ================================
// 分组管理
// ================================

function openGroupManageModal() {

    document.getElementById(
        "groupManageId"
    ).value = "";

    document.getElementById(
        "groupManageName"
    ).value = "";

    document.getElementById(
        "groupSaveText"
    ).textContent = "添加";

    document.getElementById(
        "groupCancelEdit"
    ).classList.add("hidden");

    openModal("groupManageModal");

    loadGroupManageList();
}


function closeGroupManageModal() {

    closeModal("groupManageModal");

    cancelEditGroup();
}


async function loadGroupManageList() {

    const container =
        document.getElementById(
            "groupManageList"
        );

    container.innerHTML = `
        <div class="text-center text-gray-500 py-6">
            加载中...
        </div>
    `;

    try {

        const data = await api(
            "/api/admin/groups"
        );

        const groups =
            data.items || data || [];

        renderGroupManageList(groups);

    } catch (error) {

        container.innerHTML = `
            <div class="text-center text-red-500 py-6">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


function renderGroupManageList(groups) {

    const container =
        document.getElementById(
            "groupManageList"
        );

    if (!groups.length) {

        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                暂无分组
            </div>
        `;

        return;
    }

    container.innerHTML =
        groups.map(group => `

            <div
                class="flex items-center justify-between
                       border rounded-lg p-3 bg-white">

                <div>

                    <div class="font-medium">
                        ${escapeHtml(group.name)}
                    </div>

                      ${
                          group.custom_params
                              ? `
                                  <div
                                      class="mt-1
                                            text-xs
                                            text-gray-500
                                            truncate
                                            max-w-[500px]"
                                      title="${escapeHtml(
                                          group.custom_params
                                      )}">
                                      URL 参数：
                                      ${escapeHtml(
                                          group.custom_params
                                      )}
                                  </div>
                                `
                              : `
                                  <div class="mt-1 text-xs text-gray-400">
                                      未配置 URL 参数
                                  </div>
                                `
                      }

                    <div class="text-sm text-gray-500 mt-1">
                        ${group.domain_count || 0} 个域名
                    </div>

                </div>

                <div class="flex gap-2">

                    <button
                        type="button"
                        onclick="editGroup(${group.id}, '${escapeAttr(group.name)}', '${escapeAttr(group.custom_params)}')"
                        class="px-3 py-1.5 rounded-lg
                               bg-gray-100
                               hover:bg-gray-200">
                        修改
                    </button>

                    <button
                        type="button"
                        onclick="deleteGroup(${group.id})"
                        class="px-3 py-1.5 rounded-lg
                               bg-red-50 text-red-600
                               hover:bg-red-100">
                        删除
                    </button>

                </div>

            </div>

        `).join("");
}


async function saveGroup() {

    const id =
        document.getElementById(
            "groupManageId"
        ).value;

    const name =
        document.getElementById(
            "groupManageName"
        ).value
        .trim();

    const customParams =
        document.getElementById(
            "groupManageParams"
        ).value.trim();

    if (!name) {

        showToast(
            "请输入分组名称",
            false
        );

        return;
    }


    const data = {
        name,
        custom_params: customParams,
    };


    try {

        if (id) {

            await api(
                `/api/admin/groups/${id}`,
                {
                    method: "PUT",
                    body: JSON.stringify(data),
                }
            );

            showToast("分组修改成功");

        } else {

            await api(
                "/api/admin/groups",
                {
                    method: "POST",
                    body: JSON.stringify(data),
                }
            );

            showToast("分组添加成功");
        }

        cancelEditGroup();

        await loadGroupManageList();

        await loadGroups();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}


function editGroup(id, name, custom_params) {

    document.getElementById(
        "groupManageId"
    ).value = id;

    document.getElementById(
        "groupManageName"
    ).value = name;

    document.getElementById(
        "groupManageParams"
    ).value = custom_params || "";


    document.getElementById(
        "groupSaveText"
    ).textContent = "保存";

    document.getElementById(
        "groupCancelEdit"
    ).classList.remove("hidden");

    document.getElementById(
        "groupManageName"
    ).focus();
}


function cancelEditGroup() {

    document.getElementById(
        "groupManageId"
    ).value = "";

    document.getElementById(
        "groupManageName"
    ).value = "";

    document.getElementById(
        "groupManageParams"
    ).value = "";

    document.getElementById(
        "groupSaveText"
    ).textContent = "添加";

    document.getElementById(
        "groupCancelEdit"
    ).classList.add("hidden");
}


async function deleteGroup(id) {

    if (
        !confirm(
            "确定删除这个分组吗？"
        )
    ) {
        return;
    }

    try {

        await api(
            `/api/admin/groups/${id}`,
            {
                method: "DELETE",
            }
        );

        showToast("分组删除成功");

        await loadGroupManageList();

        await loadGroups();

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}