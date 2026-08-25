
function openDomainModal() {

    document.getElementById(
        "domainModalTitle"
    ).textContent =
        "添加域名";

    document.getElementById(
        "domainForm"
    ).reset();

    document.getElementById(
        "domainId"
    ).value = "";

    document.getElementById(
        "enabled"
    ).checked = true;

    document.getElementById(
        "poolList"
    ).innerHTML = "";

    updateJumpType();

    openModal(
        "domainModal"
    );
}




function updateJumpType() {

    const type =
        document.getElementById(
            "jumpType"
        ).value;

    const target =
        document.getElementById(
            "targetBox"
        );

    const pool =
        document.getElementById(
            "poolBox"
        );

    if (type === "random") {

        target.classList.add(
            "hidden"
        );

        pool.classList.remove(
            "hidden"
        );

    } else {

        target.classList.remove(
            "hidden"
        );

        pool.classList.add(
            "hidden"
        );
    }
}



// function updateJumpType() {

//     const type =
//         document.getElementById(
//             "jumpType"
//         ).value;

//     const target =
//         document.getElementById(
//             "targetBox"
//         );

//     const pool =
//         document.getElementById(
//             "poolBox"
//         );

//     if (type === "random") {

//         target.classList.add(
//             "hidden"
//         );

//         pool.classList.remove(
//             "hidden"
//         );

//     } else {

//         target.classList.remove(
//             "hidden"
//         );

//         pool.classList.add(
//             "hidden"
//         );
//     }
// }


function addPoolItem(
    item = {
        target_domain: "",
        weight: 1,
        enabled: true,
    }
) {

    const container =
        document.getElementById(
            "poolList"
        );

    const div =
        document.createElement(
            "div"
        );

    div.className =
        "pool-item";

    div.innerHTML = `
        <input
            class="admin-input pool-domain"
            value="${escapeAttr(
                item.target_domain
            )}"
            placeholder="https://example.com">

        <input
            class="admin-input pool-weight"
            type="number"
            min="1"
            value="${item.weight}">

        <label
            class="flex items-center gap-2 mb-0">

            <input
                class="pool-enabled"
                type="checkbox"
                ${
                    item.enabled
                        ? "checked"
                        : ""
                }>

            启用

        </label>

        <button
            type="button"
            class="pool-remove"
            onclick="
                this.parentElement.remove()
            ">

            ×

        </button>
    `;

    container.appendChild(
        div
    );
}