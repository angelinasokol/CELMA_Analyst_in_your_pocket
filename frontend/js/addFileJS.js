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
    uploadCard.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", handleFile);
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
        uploadStatus.textContent = "Файл превышает 10 МБ";
        return;
    }
    
    const allowedExtensions = ["csv", "xlsx", "xml"];
    const extension = file.name.split(".").pop().toLowerCase();
    
    if (!allowedExtensions.includes(extension)) {
        uploadStatus.textContent = "Неподдерживаемый формат файла";
        return;
    }

    uploadStatus.textContent = "📖 Читаем файл...";
    
    try {
        const data = await parseFile(file, extension);
        
        // 🔍 Простая аналитика "на лету"
        const analytics = {
            fileName: file.name,
            fileSize: file.size,
            rowsCount: data.length,
            headers: data[0] || [],
            preview: data.slice(0, 10), // первые 10 строк для предпросмотра
            processedAt: new Date().toISOString()
        };
        
        uploadStatus.textContent = "✅ Готово! Переходим к анализу...";
        
        // Сохраняем в sessionStorage и переходим
        sessionStorage.setItem('celma_analytics', JSON.stringify(analytics));
        sessionStorage.setItem('celma_raw_data', JSON.stringify(data)); // если нужно на дашборде
        
        setTimeout(() => {
            window.location.href = "processing.html";
        }, 800);
        
    } catch (error) {
        console.error("Ошибка парсинга:", error);
        uploadStatus.textContent = "❌ Ошибка: " + error.message;
    }
}

// Универсальный парсер
function parseFile(file, extension) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                let result = [];
                
                if (extension === 'csv') {
                    // Простой CSV-парсер (для продакшена лучше PapaParse)
                    const text = e.target.result;
                    result = text.split('\n')
                        .filter(row => row.trim())
                        .map(row => row.split(',').map(cell => cell.trim()));
                        
                } else if (extension === 'xlsx') {
                    const workbook = XLSX.read(e.target.result, { type: 'array' });
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    result = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
                    
                } else if (extension === 'xml') {
                    const parser = new DOMParser();
                    const xmlDoc = parser.parseFromString(e.target.result, "text/xml");
                    // 🎯 Тут нужна логика под твою структуру 1С
                    // Пока заглушка:
                    result = [["XML-файл загружен", "Требуется спецификация структуры"]];
                }
                
                resolve(result);
            } catch (err) {
                reject(err);
            }
        };
        
        reader.onerror = () => reject(new Error("Не удалось прочитать файл"));
        
        // Читаем в нужном формате
        if (extension === 'xlsx') {
            reader.readAsArrayBuffer(file);
        } else {
            reader.readAsText(file, 'utf-8');
        }
    });
}

});