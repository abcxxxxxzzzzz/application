async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);

    if (response.status === 401) {
        window.location.href = "/login";
        return null;
    }

    return response;
}


async function apiJson(url, options = {}) {
    const response = await apiFetch(url, options);

    if (!response) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "请求失败"
        );
    }

    return data;
}


function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


function formatDate(value) {
    if (!value) {
        return "-";
    }

    return new Date(value).toLocaleString("zh-CN");
}


async function logout() {
    await fetch(
        "/api/auth/logout",
        {
            method: "POST",
        }
    );

    window.location.href = "/login";
}