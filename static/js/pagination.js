document.addEventListener("DOMContentLoaded", function () {
    const productosContainer = document.getElementById("productos-grid");
    const paginacionContainer = document.getElementById("pagination-container");
    const loadingSpinner = document.getElementById("loading-spinner");

    function showLoading() {
        if (loadingSpinner) {
            loadingSpinner.classList.remove("hidden");
        }
        if (productosContainer) {
            productosContainer.style.opacity = "0.5";
            productosContainer.style.pointerEvents = "none";
        }
    }

    function hideLoading() {
        if (loadingSpinner) {
            loadingSpinner.classList.add("hidden");
        }
        if (productosContainer) {
            productosContainer.style.opacity = "1";
            productosContainer.style.pointerEvents = "auto";
        }
    }

    function setupPaginationListeners() {
        if (!paginacionContainer) return;

        const paginationLinks = paginacionContainer.querySelectorAll("a[href]");
        paginationLinks.forEach((link) => {
            link.removeEventListener("click", handlePaginationClick);
            link.addEventListener("click", handlePaginationClick);
        });
    }

    async function handlePaginationClick(event) {
        event.preventDefault();

        const href = this.getAttribute("href");
        const url = new URL(href, window.location.href).toString();

        showLoading();

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error("No se pudo cargar la pagina solicitada.");
            }

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");

            const newProductosContainer = doc.getElementById("productos-grid");
            const newPaginacionContainer = doc.getElementById("pagination-container");

            if (newProductosContainer && productosContainer) {
                productosContainer.innerHTML = newProductosContainer.innerHTML;
            }

            if (newPaginacionContainer && paginacionContainer) {
                paginacionContainer.innerHTML = newPaginacionContainer.innerHTML;
            }

            setupPaginationListeners();

            if (typeof initProductAnimations === "function") {
                initProductAnimations();
            }
        } catch (error) {
            console.error("Error al cargar la paginacion:", error);
        } finally {
            hideLoading();
        }
    }

    setupPaginationListeners();
});
