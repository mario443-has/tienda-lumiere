document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.getElementById("announcement-carousel");
    const carouselWrapper = document.getElementById("announcement-carousel-wrapper");
    const prevBtn = document.getElementById("prev-announcement");
    const nextBtn = document.getElementById("next-announcement");
    const indicators = document.querySelectorAll("#carousel-indicators .indicator");

    let currentIndex = 0;
    let autoSlideInterval;
    const autoSlideDelay = 5000;
    let isTransitioning = false;
    let items = [];
    let slideCount = 0;
    let infiniteLoop = false;

    function getSlideWidth() {
        return carouselWrapper ? carouselWrapper.clientWidth : 0;
    }

    function layoutSlides() {
        const width = getSlideWidth();
        if (!width) return;

        items.forEach((item) => {
            item.style.flex = `0 0 ${width}px`;
            item.style.width = `${width}px`;
            item.style.maxWidth = `${width}px`;
        });
    }

    function updateIndicators(realIndex) {
        indicators.forEach((indicator) => indicator.classList.remove("opacity-100"));
        if (indicators[realIndex]) {
            indicators[realIndex].classList.add("opacity-100");
        }
    }

    function updateCarousel(index, animate = true) {
        if (!carousel || items.length === 0) return;

        const offset = index * getSlideWidth();
        carousel.style.transition = animate ? "transform 0.5s ease-in-out" : "none";
        carousel.style.transform = `translate3d(-${offset}px, 0, 0)`;

        let realIndex = index;
        if (infiniteLoop) {
            realIndex = (index - 1 + slideCount) % slideCount;
        }
        updateIndicators(realIndex);
    }

    function cloneSlides() {
        const originals = carousel.querySelectorAll(".carousel-item:not(.clone)");
        if (originals.length < 2) return;

        const firstClone = originals[0].cloneNode(true);
        const lastClone = originals[originals.length - 1].cloneNode(true);
        firstClone.classList.add("clone");
        lastClone.classList.add("clone");
        firstClone.setAttribute("aria-hidden", "true");
        lastClone.setAttribute("aria-hidden", "true");

        carousel.appendChild(firstClone);
        carousel.insertBefore(lastClone, originals[0]);

        infiniteLoop = true;
        currentIndex = 1;
    }

    function goToSlide(index) {
        if (isTransitioning || items.length === 0) return;

        isTransitioning = true;

        if (infiniteLoop) {
            currentIndex = index;
        } else {
            currentIndex = Math.max(0, Math.min(index, items.length - 1));
        }

        updateCarousel(currentIndex, true);
        resetAutoSlide();
    }

    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    function prevSlide() {
        goToSlide(currentIndex - 1);
    }

    function startAutoSlide() {
        if (slideCount < 2) return;
        stopAutoSlide();
        autoSlideInterval = setInterval(nextSlide, autoSlideDelay);
    }

    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }

    function resetAutoSlide() {
        stopAutoSlide();
        startAutoSlide();
    }

    function handleTransitionEnd(event) {
        if (event.target !== carousel || event.propertyName !== "transform") return;

        if (infiniteLoop && items[currentIndex]?.classList.contains("clone")) {
            carousel.style.transition = "none";
            if (currentIndex === 0) {
                currentIndex = items.length - 2;
            } else {
                currentIndex = 1;
            }
            updateCarousel(currentIndex, false);
            carousel.offsetHeight;
        }

        isTransitioning = false;
    }

    function initAnnouncementCarousel() {
        if (!carousel || !carouselWrapper || carousel.dataset.initialized === "true") {
            return;
        }
        carousel.dataset.initialized = "true";

        items = [...carousel.querySelectorAll(".carousel-item:not(.clone)")];
        slideCount = items.length;

        if (slideCount === 0) return;

        cloneSlides();
        items = [...carousel.querySelectorAll(".carousel-item")];
        layoutSlides();
        updateCarousel(currentIndex, false);

        carousel.addEventListener("transitionend", handleTransitionEnd);

        prevBtn?.addEventListener("click", prevSlide);
        nextBtn?.addEventListener("click", nextSlide);

        indicators.forEach((dot, index) => {
            dot.addEventListener("click", () => {
                goToSlide(infiniteLoop ? index + 1 : index);
            });
        });

        carousel.addEventListener("mouseenter", stopAutoSlide);
        carousel.addEventListener("mouseleave", startAutoSlide);

        let startX = 0;
        let isDragging = false;
        const dragThreshold = 50;

        carouselWrapper.addEventListener(
            "touchstart",
            (event) => {
                startX = event.touches[0].clientX;
                isDragging = true;
                stopAutoSlide();
            },
            { passive: true }
        );

        carouselWrapper.addEventListener(
            "touchmove",
            (event) => {
                if (!isDragging) return;

                const diffX = event.touches[0].clientX - startX;
                if (Math.abs(diffX) > dragThreshold) {
                    if (diffX < 0) {
                        nextSlide();
                    } else {
                        prevSlide();
                    }
                    isDragging = false;
                }
            },
            { passive: true }
        );

        carouselWrapper.addEventListener("touchend", () => {
            isDragging = false;
            startAutoSlide();
        });

        carouselWrapper.addEventListener("touchcancel", () => {
            isDragging = false;
            startAutoSlide();
        });

        const resizeObserver = new ResizeObserver(() => {
            layoutSlides();
            updateCarousel(currentIndex, false);
        });
        resizeObserver.observe(carouselWrapper);

        startAutoSlide();
    }

    if (carousel && carouselWrapper && indicators.length > 0) {
        initAnnouncementCarousel();
    }

    const categoryCarousel = document.getElementById("category-carousel");
    const prevCategory = document.getElementById("prev-category");
    const nextCategory = document.getElementById("next-category");
    const categoryIndicators = document.querySelectorAll("#category-carousel-indicators .indicator");
    let currentCategory = 0;

    function updateCategoryCarousel(index) {
        if (!categoryCarousel) return;

        const item = categoryCarousel.querySelector(".carousel-item");
        if (!item) return;

        categoryCarousel.scrollLeft = item.clientWidth * index;
        categoryIndicators.forEach((indicator) => indicator.classList.remove("opacity-100"));
        if (categoryIndicators[index]) {
            categoryIndicators[index].classList.add("opacity-100");
        }
    }

    if (categoryCarousel) {
        prevCategory?.addEventListener("click", () => {
            currentCategory =
                (currentCategory - 1 + categoryIndicators.length) % categoryIndicators.length;
            updateCategoryCarousel(currentCategory);
        });

        nextCategory?.addEventListener("click", () => {
            currentCategory = (currentCategory + 1) % categoryIndicators.length;
            updateCategoryCarousel(currentCategory);
        });

        categoryIndicators.forEach((indicator, index) => {
            indicator.addEventListener("click", () => {
                currentCategory = index;
                updateCategoryCarousel(currentCategory);
            });
        });

        updateCategoryCarousel(currentCategory);
    }
});
