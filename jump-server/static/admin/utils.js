// 工具函数

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
    return escapeHtml(value);
}

// 通知
let toastTimer = null;

function showToast(message, success = true) {

    const el =
        document.getElementById("toast");

    if (!el) return;

    clearTimeout(toastTimer);

    el.textContent = message;

    el.className =
        "fixed top-6 left-1/2 " +
        "-translate-x-1/2 " +
        "z-[99999] " +
        "px-4 py-2.5 " +
        "rounded-lg " +
        "shadow-lg " +
        (success
            ? "toast-success"
            : "toast-error");

    toastTimer = setTimeout(() => {
        el.classList.add("hidden");
    }, 2000);
}

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


// 获取选择框ID
function getSelectedIds() {
    return [
        ...document.querySelectorAll(
            ".domain-check:checked"
        ),
    ].map(
        el => Number(el.value)
    );
}


// 分页切换
function changePageSize(size) {

    state.pageSize = Number(size);

    state.page = 1;

    loadDomains();
}



// 加载动画JS
function showDomainLoading() {

    const loading =
        document.getElementById(
            "domainTableLoading"
        );

    if (loading) {
        loading.classList.remove(
            "hidden"
        );
    }
}


function hideDomainLoading() {

    const loading =
        document.getElementById(
            "domainTableLoading"
        );

    if (loading) {
        loading.classList.add(
            "hidden"
        );
    }
}







document.addEventListener("mouseover", function (event) {

    const target =
        event.target.closest(
            ".url-tooltip-trigger"
        );

    if (!target) {
        return;
    }

    let tooltip =
        document.getElementById(
            "globalUrlTooltip"
        );

    if (!tooltip) {

        tooltip =
            document.createElement("div");

        tooltip.id =
            "globalUrlTooltip";

        tooltip.className =
            "fixed z-[999999] hidden " +
            "w-[600px] max-w-[80vw] " +
            "px-4 py-3 rounded-lg " +
            "bg-gray-900 text-white " +
            "text-xs leading-5 " +
            "shadow-2xl break-all " +
            "whitespace-normal " +
            "pointer-events-none";

        document.body.appendChild(
            tooltip
        );
    }

    tooltip.textContent =
        target.dataset.tooltip;

    const rect =
        target.getBoundingClientRect();

    tooltip.style.left =
        `${rect.left}px`;

    tooltip.style.top =
        `${rect.bottom + 8}px`;

    tooltip.classList.remove(
        "hidden"
    );
});


document.addEventListener("mouseout", function (event) {

    const target =
        event.target.closest(
            ".url-tooltip-trigger"
        );

    if (!target) {
        return;
    }

    const tooltip =
        document.getElementById(
            "globalUrlTooltip"
        );

    if (tooltip) {
        tooltip.classList.add(
            "hidden"
        );
    }
});