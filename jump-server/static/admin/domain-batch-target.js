function openBatchTargetUpdateModal() {

    const oldInput =
        document.getElementById(
            "batchOldTargetDomain"
        );

    const newInput =
        document.getElementById(
            "batchNewTargetDomain"
        );

    oldInput.value = "";
    newInput.value = "";

    openModal(
        "batchTargetUpdateModal"
    );

    setTimeout(() => {
        oldInput.focus();
    }, 50);
}


async function submitBatchTargetUpdate() {

    const oldInput =
        document.getElementById(
            "batchOldTargetDomain"
        );

    const newInput =
        document.getElementById(
            "batchNewTargetDomain"
        );

    const oldTarget =
        oldInput.value.trim();

    const newTarget =
        newInput.value.trim();


    if (!oldTarget) {

        showToast(
            "请输入原目标地址",
            false
        );

        oldInput.focus();

        return;
    }


    if (!newTarget) {

        showToast(
            "请输入新目标地址",
            false
        );

        newInput.focus();

        return;
    }


    if (oldTarget === newTarget) {

        showToast(
            "新旧目标地址不能相同",
            false
        );

        return;
    }


    if (
        !confirm(
            `确定将目标地址\n\n${oldTarget}\n\n更新为\n\n${newTarget} 吗？`
        )
    ) {
        return;
    }


    try {

        const result =
            await api(
                "/api/admin/domains/batch-update-target",
                {
                    method: "POST",
                    body: JSON.stringify({
                        old_target_domain:
                            oldTarget,

                        new_target_domain:
                            newTarget,
                    }),
                }
            );


        closeModal(
            "batchTargetUpdateModal"
        );


        showToast(
            `成功更新 ${result.updated} 个域名`
        );


        await loadDomains();


    } catch (error) {

        showToast(
            error.message,
            false
        );
    }
}





