function openModal(id) {
    const el =
        document.getElementById(id);

    if (!el) return;

    el.classList.remove("hidden");
}

function closeModal(id) {
    const el =
        document.getElementById(id);

    if (!el) return;

    el.classList.add("hidden");
}