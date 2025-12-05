document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const toggle = document.querySelector("[data-toggle-sidebar]");
    if (toggle && sidebar) {
        toggle.addEventListener("click", () => {
            sidebar.classList.toggle("is-hidden");
        });
    }
});
