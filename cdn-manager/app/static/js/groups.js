let groups = [];


// ============================================================
// 加载分组
// ============================================================

async function loadGroups() {
    try {
        const data = await apiJson(
            "/api/groups"
        );

        if (!data) {
            return;
        }

        groups = data;

        renderGroups();

    } catch (error) {

        console.error(error);

        alert(
            error.message || "加载分组失败"
        );
    }
}


// ============================================================
// 渲染分组
// ============================================================

function renderGroups() {

    const tbody = document.getElementById(
        "groupsTableBody"
    );

    if (!tbody) {
        console.error(
            "找不到 #groupsTableBody"
        );
        return;
    }


    if (!groups.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="text-center text-gray-400 py-12"
                >
                    暂无分组
                </td>
            </tr>
        `;

        return;
    }


    tbody.innerHTML = groups
        .map(group => `
            <tr class="border-b last:border-b-0">

                <td class="px-6 py-4 text-sm">
                    ${group.id}
                </td>

                <td class="px-6 py-4 font-medium">
                    ${escapeHtml(group.name)}
                </td>


                <td class="px-6 py-4 text-sm text-gray-500">
                    ${formatDate(group.created_at)}
                </td>

                <td class="px-6 py-4 text-right">

                    <button
                        onclick="editGroup(${group.id})"
                        class="text-blue-600 mr-4 hover:text-blue-800"
                    >
                        编辑
                    </button>

                    <button
                        onclick="deleteGroup(${group.id})"
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
// 打开分组弹窗
// ============================================================

function openGroupModal(group = null) {

    const modal = document.getElementById(
        "groupModal"
    );

    const title = document.getElementById(
        "groupModalTitle"
    );

    const idInput = document.getElementById(
        "groupId"
    );

    const nameInput = document.getElementById(
        "groupName"
    );



    if (!modal || !title || !idInput || !nameInput) {

        console.error(
            "分组弹窗元素不存在"
        );

        return;
    }


    if (group) {

        title.textContent = "编辑分组";

        idInput.value = group.id;

        nameInput.value = group.name;


    } else {

        title.textContent = "新建分组";

        idInput.value = "";

        nameInput.value = "";

    }


    modal.classList.remove("hidden");

    modal.classList.add("flex");
}


// ============================================================
// 关闭分组弹窗
// ============================================================

function closeGroupModal() {

    const modal = document.getElementById(
        "groupModal"
    );

    if (!modal) {
        return;
    }

    modal.classList.add("hidden");

    modal.classList.remove("flex");
}


// ============================================================
// 编辑分组
// ============================================================

function editGroup(id) {

    const group = groups.find(
        item => item.id === id
    );

    if (!group) {

        alert("分组不存在");

        return;
    }


    openGroupModal(group);
}


// ============================================================
// 保存分组
// ============================================================

async function saveGroup(event) {

    event.preventDefault();


    const id = document.getElementById(
        "groupId"
    ).value;


    const name = document.getElementById(
        "groupName"
    ).value
        .trim();




    if (!name) {

        alert("请输入分组名称");

        return;
    }



    const data = {
        name: name,
    };


    try {

        if (id) {

            await apiJson(
                `/api/groups/${id}`,
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

            await apiJson(
                "/api/groups",
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


        closeGroupModal();

        await loadGroups();


        alert(
            id
                ? "分组修改成功"
                : "分组创建成功"
        );


    } catch (error) {

        console.error(error);

        alert(
            error.message || "保存分组失败"
        );
    }
}


// ============================================================
// 删除分组
// ============================================================

async function deleteGroup(id) {

    const group = groups.find(
        item => item.id === id
    );


    if (!group) {

        alert("分组不存在");

        return;
    }


    if (
        !confirm(
            `确定删除分组「${group.name}」吗？`
        )
    ) {
        return;
    }


    try {

        await apiJson(
            `/api/groups/${id}`,
            {
                method: "DELETE",
            }
        );


        await loadGroups();


        alert("分组删除成功");


    } catch (error) {

        console.error(error);

        alert(
            error.message || "删除分组失败"
        );
    }
}


// ============================================================
// 表单提交
// ============================================================

const groupForm = document.getElementById(
    "groupForm"
);


if (groupForm) {

    groupForm.addEventListener(
        "submit",
        saveGroup
    );
}


// ============================================================
// 页面初始化
// ============================================================

loadGroups();