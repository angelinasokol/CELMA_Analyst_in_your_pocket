document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 DOM загружен. Инициализация CELMA...");

    const uploadCard = document.querySelector(".upload-card");
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");
    const uploadStatus = document.getElementById("uploadStatus");

    if (!uploadCard || !fileInput) return;

    // Блокировка форм
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', e => { e.preventDefault(); e.stopPropagation(); return false; });
        form.setAttribute('onsubmit', 'return false;');
    });

    // Клик по карточке
    uploadCard.addEventListener("click", (e) => {
        if (e.target !== browseBtn && e.target !== fileInput) {
            fileInput.click();
        }
    });

    // Клик по кнопке
    if (browseBtn) {
        browseBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileInput.click();
        });
    }

    // Выбор файла
    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            processFile(fileInput.files[0]);
        }
        fileInput.value = ''; 
    });

    // Drag & Drop
    uploadCard.addEventListener("dragover", (e) => { e.preventDefault(); uploadCard.classList.add("dragover"); });
    uploadCard.addEventListener("dragleave", (e) => { e.preventDefault(); uploadCard.classList.remove("dragover"); });
    uploadCard.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadCard.classList.remove("dragover");
        if (e.dataTransfer.files.length) processFile(e.dataTransfer.files[0]);
    });

    async function processFile(file) {
        if (uploadStatus) uploadStatus.textContent = "📤 Загрузка файла...";

        try {
            // БЕЗ ПРОБЕЛОВ!
            const API_URL = "https://friendly-halibut-rjpgrj4pvqq24g4-8000.app.github.dev";
            
            // --- ШАГ 1: ЗАГРУЗКА ФАЙЛА ---
            const formData = new FormData();
            formData.append("file", file);

            const uploadResponse = await fetch(`${API_URL}/upload/`, { method: "POST", body: formData });
            if (!uploadResponse.ok) throw new Error(`Ошибка загрузки: ${uploadResponse.status}`);
            
            const uploadResult = await uploadResponse.json();
            const fileId = uploadResult.file_id;
            console.log("✅ Файл загружен, ID:", fileId);

            if (uploadStatus) uploadStatus.textContent = "🧠 Нейросеть анализирует...";

            // --- ШАГ 2: ЗАПРОС АНАЛИТИКИ (ЭТОГО НЕ ХВАТАЛО!) ---
            // Сразу после загрузки спрашиваем у бэкенда полный разбор файла
            const analyticsResponse = await fetch(`${API_URL}/analytics/${fileId}`, { method: "POST" });
            
            if (!analyticsResponse.ok) {
                // Если аналитика упала, пробуем продолжить хотя бы с базовыми данными
                console.warn("⚠️ Аналитика не удалась, используем базовые данные");
                var fullData = uploadResult; 
            } else {
                var fullData = await analyticsResponse.json();
                console.log("📊 Полные данные аналитики получены:", fullData);
            }

            // Добавляем имя файла в данные аналитики (так как бэкенд может его не вернуть в analyze)
            fullData.filename = file.name;

            // Сохраняем ПОЛНЫЕ данные (с графиками и прогнозами)
            sessionStorage.setItem("celma_file_id", fileId);
            sessionStorage.setItem("celma_analytics", JSON.stringify(fullData));

            if (uploadStatus) {
                uploadStatus.textContent = "✅ Готово! Переходим...";
                uploadStatus.style.color = "#2E7D32";
            }

            // Переход
            setTimeout(() => {
                window.location.href = "processing.html";
            }, 800);

        } catch (error) {
            console.error("💥 Ошибка:", error);
            if (uploadStatus) {
                uploadStatus.textContent = "❌ " + error.message;
                uploadStatus.style.color = "#d32f2f";
            }
        }
    }
});