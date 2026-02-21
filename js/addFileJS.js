const fileInput = document.getElementById("fileInput");

fileInput.addEventListener("change", function () {
    if (this.files.length > 0) {
        window.location.href = "/addFile.html";
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    const prevBtn = document.querySelector(".slider-arrow.prev");
    const nextBtn = document.querySelector(".slider-arrow.next");
    const currentSlideText = document.querySelector(".current-slide");
    const totalSlidesText = document.querySelector(".total-slides");

    let currentIndex = 0;
    const totalSlides = slides.length;
    totalSlidesText.textContent = totalSlides;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle("active", i === index);
        });
        dots.forEach((dot, i) => {
            dot.classList.toggle("active", i === index);
        });
        currentSlideText.textContent = index + 1;
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % totalSlides;
        showSlide(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        showSlide(currentIndex);
    }

    nextBtn.addEventListener("click", nextSlide);
    prevBtn.addEventListener("click", prevSlide);

    dots.forEach(dot => {
        dot.addEventListener("click", () => {
            currentIndex = parseInt(dot.dataset.index);
            showSlide(currentIndex);
        });
    });

    showSlide(currentIndex);
});
document.addEventListener("DOMContentLoaded", () => {

    const uploadCard = document.querySelector(".upload-card");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");

    if (!uploadCard || !fileInput) return;

    /* =========================
       Клик по карточке
    ========================== */
    uploadCard.addEventListener("click", () => {
        fileInput.click();
    });

    /* =========================
       Выбор файла
    ========================== */
    fileInput.addEventListener("change", handleFile);

    /* =========================
       Drag & Drop
    ========================== */
    uploadCard.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadCard.classList.add("dragover");
    });

    uploadCard.addEventListener("dragleave", () => {
        uploadCard.classList.remove("dragover");
    });

    uploadCard.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadCard.classList.remove("dragover");

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    });

    function handleFile() {
        if (fileInput.files.length > 0) {
            processFile(fileInput.files[0]);
        }
    }

    /* =========================
       Основная обработка
    ========================== */
    function processFile(file) {

        // Проверка размера (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            uploadStatus.textContent = "Файл превышает 10 МБ";
            return;
        }

        // Проверка формата
        const allowedExtensions = ["csv", "xlsx", "xml"];
        const extension = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) {
            uploadStatus.textContent = "Неподдерживаемый формат файла";
            return;
        }

        uploadStatus.textContent = "Файл загружен. Подготавливаем анализ...";

        // Имитация обработки
        setTimeout(() => {
            window.location.href = "processing.html";
        }, 1000);
    }

});