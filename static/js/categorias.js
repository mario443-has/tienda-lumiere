document.addEventListener("DOMContentLoaded", function () {
    const dropdownBtn = document.querySelector(".categorias-dropdown-btn");
    const categoriasList = document.querySelector(".categorias-lista");
    const categoriaItems = document.querySelectorAll(".categoria-item");

    if (dropdownBtn) {
        dropdownBtn.addEventListener("click", function () {
            this.classList.toggle("active");
            categoriasList?.classList.toggle("show");
        });
    }

    if (window.innerWidth <= 768) {
        categoriaItems.forEach((item) => {
            const link = item.querySelector(".categoria-link");
            const subcategorias = item.querySelector(".subcategorias");

            if (link && subcategorias) {
                link.addEventListener("click", function (event) {
                    if (window.innerWidth <= 768) {
                        event.preventDefault();
                        item.classList.toggle("active");
                    }
                });
            }
        });
    }

    document.addEventListener("click", function (event) {
        const shouldClose =
            !event.target.closest(".categorias-nav") &&
            categoriasList &&
            categoriasList.classList.contains("show");

        if (shouldClose) {
            dropdownBtn?.classList.remove("active");
            categoriasList.classList.remove("show");
        }
    });

    let resizeTimeout;
    let lastWidth = window.innerWidth;

    window.addEventListener("resize", function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function () {
            const newWidth = window.innerWidth;
            const crossedBreakpoint =
                (lastWidth <= 768 && newWidth > 768) ||
                (lastWidth > 768 && newWidth <= 768);

            if (crossedBreakpoint) {
                location.reload();
            }
            lastWidth = newWidth;
        }, 200);
    });

    window.addEventListener("orientationchange", function () {
        location.reload();
    });
});
