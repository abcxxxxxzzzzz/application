// 负责添加、编辑、删除域名
function getPool() {

    return [
        ...document.querySelectorAll(
            "#poolList .pool-item"
        ),
    ].map(row => ({
        target_domain:
            row.querySelector(
                ".pool-domain"
            ).value.trim(),

        weight:
            Number(
                row.querySelector(
                    ".pool-weight"
                ).value
            ),

        enabled:
            row.querySelector(
                ".pool-enabled"
            ).checked,
    }));
}



async function submitDomain(event) {
    event.preventDefault();

    const id = document.getElementById("domainId").value;
    const type = document.getElementById("jumpType").value;
    const useGroupParams = document.getElementById("useGroupParams").checked;

    const data = {
        domain: document.getElementById("domain").value.trim(),
        group_id: Number(
            document.getElementById("groupId").value
        ),
        jump_type: type,
        jump_method: document.getElementById("jumpMethod").value,
        status_code: Number(
            document.getElementById("statusCode").value
        ),
        target_domain:
            type === "random"
                ? null
                : document.getElementById("targetDomain").value.trim() || null,
        embedded_code: document.getElementById("embeddedCode").value.trim() || null,
        enabled: document.getElementById("enabled").checked,
        use_group_params: useGroupParams,
        pool:
            type === "random"
                ? getPool()
                : [],
    };

    if (!data.domain) {
        showToast("请输入域名", false);
        return;
    }

    if (!data.group_id) {
        showToast("请选择分组", false);
        return;
    }

    try {
        const result = await api(
            id
                ? `/api/admin/domains/${id}`
                : "/api/admin/domains",
            {
                method: id ? "PUT" : "POST",
                body: JSON.stringify(data),
            }
        );

        closeModal("domainModal");

        showToast(
            id
                ? "域名修改成功"
                : "域名添加成功"
        );

        await loadDomains();

    } catch (error) {
        showToast(
            error.message,
            false
        );
    }
}


async function editDomain(id) {

    const item = state.domains.find(
        x => x.id === id
    );

    if (!item) {
        showToast("域名不存在", false);
        return;
    }

    document.getElementById(
        "domainModalTitle"
    ).textContent = "编辑域名";

    document.getElementById(
        "domainId"
    ).value = item.id;

    document.getElementById(
        "domain"
    ).value = item.domain;

    document.getElementById(
        "groupId"
    ).value = item.group_id;

    document.getElementById(
        "jumpType"
    ).value = item.jump_type;

    document.getElementById(
        "jumpMethod"
    ).value = item.jump_method;

    document.getElementById(
        "statusCode"
    ).value = item.status_code;

    document.getElementById(
        "targetDomain"
    ).value = item.target_domain || "";

    document.getElementById(
        "embeddedCode"
    ).value = item.embedded_code || "";

    document.getElementById(
        "enabled"
    ).checked = item.enabled;

    document.getElementById(
        "useGroupParams"
    ).checked = !!item.use_group_params;

    document.getElementById(
        "poolList"
    ).innerHTML = "";

    for (const pool of item.pool || []) {
        addPoolItem(pool);
    }

    updateJumpType();

    openModal("domainModal");
}


async function deleteDomain(id) {

    const item = state.domains.find(
        x => x.id === id
    );

    const name =
        item?.domain || "这个域名";

    if (
        !confirm(
            `确定删除 ${name} 吗？`
        )
    ) {
        return;
    }

    try {

        await api(
            `/api/admin/domains/${id}`,
            {
                method: "DELETE",
            }
        );

        showToast("删除成功");

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}