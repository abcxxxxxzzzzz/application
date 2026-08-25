function openBatchStatusModal() {

    const ids = getSelectedIds();

    if (!ids.length) {

        showToast(
            "请先勾选要修改的域名",
            false
        );

        return;
    }

    document.getElementById(
        "batchStatusSelected"
    ).textContent =
        `已选择 ${ids.length} 个域名`;

    document.getElementById(
        "batchStatusCode"
    ).value = "302";

    openModal(
        "batchStatusModal"
    );
}


async function submitBatchStatus() {

    const ids = getSelectedIds();

    if (!ids.length) {

        showToast(
            "请先勾选要修改的域名",
            false
        );

        return;
    }

    const statusCode =
        Number(
            document.getElementById(
                "batchStatusCode"
            ).value
        );

    if (!statusCode) {

        showToast(
            "请选择状态码",
            false
        );

        return;
    }

    if (
        !confirm(
            `确定将 ${ids.length} 个域名的状态码修改为 ${statusCode} 吗？`
        )
    ) {
        return;
    }

    try {

        const result =
            await api(
                "/api/admin/domains/batch-status",
                {
                    method: "POST",
                    body: JSON.stringify({
                        ids,
                        status_code: statusCode,
                    }),
                }
            );

        closeModal(
            "batchStatusModal"
        );

        showToast(
            `成功修改 ${result.updated} 个域名`
        );

        await loadDomains();

    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}