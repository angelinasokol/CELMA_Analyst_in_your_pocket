const API_URL = "https://friendly-halibut-rjpgrj4pvqq24g4-8000.app.github.dev";
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
    
    // Клик по карточке
    uploadCard.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });

    // Выбор файла
    fileInput.addEventListener("change", (e) => {
        e.preventDefault();
        e.stopPropagation();
        handleFile();
    });
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

    async function processFile(file) {
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            uploadStatus.textContent = "❌ Файл превышает 10 МБ";
            return;
        }
        
        const allowedExtensions = ["csv", "xlsx", "xml"];
        const extension = file.name.split(".").pop().toLowerCase();
        
        if (!allowedExtensions.includes(extension)) {
            uploadStatus.textContent = "❌ Неподдерживаемый формат файла";
            return;
        }

        uploadStatus.textContent = "📤 Загружаем файл...";
        
        try {
            // ШАГ 1: Загрузка файла
            const formData = new FormData();
            formData.append("file", file);

            const uploadResponse = await fetch(`${API_URL}/upload/`, {
                method: "POST",
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error(`Ошибка загрузки: ${uploadResponse.status}`);
            }

            const uploadResult = await uploadResponse.json();
            const fileId = uploadResult.file_id;
            
            console.log("✅ Файл загружен:", fileId);
            uploadStatus.textContent = "📊 Анализируем...";

            // ШАГ 2: Получение аналитики
            const analyticsResponse = await fetch(`${API_URL}/analytics/${fileId}`, {
                method: "POST"
            });

            if (!analyticsResponse.ok) {
                throw new Error("Ошибка аналитики: " + analyticsResponse.status);
            }

            const analyticsData = await analyticsResponse.json();
            console.log("✅ Аналитика:", analyticsData);

            // ШАГ 3: Сохранение
            const analytics = {
                fileId: fileId,
                fileName: file.name,
                fileSize: file.size,
                ...analyticsData,
                processedAt: new Date().toISOString()
            };
            
            sessionStorage.setItem('celma_analytics', JSON.stringify(analytics));
            sessionStorage.setItem('celma_file_id', fileId);
            
            console.log("💾 Сохранено в sessionStorage");
            uploadStatus.textContent = "✅ Готово! Переходим...";
            
            
            window.location.href = "processing.html";
        } catch (error) {
            console.error("❌ Ошибка:", error);
            uploadStatus.textContent = "❌ " + error.message;
        }
    }
});