document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 DOM загружен. Инициализация CELMA...");

    const uploadCard = document.querySelector(".upload-card");
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn"); // Новая кнопка
    const uploadStatus = document.getElementById("uploadStatus");

    if (!uploadCard || !fileInput) {
        console.error("❌ ОШИБКА: Основные элементы не найдены!");
        return;
    }

    // Блокировка форм
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => { e.preventDefault(); e.stopPropagation(); return false; });
        form.setAttribute('onsubmit', 'return false;');
    });

    // --- ОБРАБОТЧИКИ КЛИКОВ ---
    
    // 1. Клик по всей карточке
    if (uploadCard) {
        uploadCard.addEventListener("click", (e) => {
            // Если клик был не по кнопке и не по инпуту, то открываем выбор файла
            if (e.target !== browseBtn && e.target !== fileInput) {
                console.log("👆 Клик по карточке");
                fileInput.click();
            }
        });
    }

    // 2. Клик по новой кнопке "Browse File"
    if (browseBtn) {
        browseBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log("🖱️ Клик по кнопке Browse File");
            fileInput.click();
        });
    }

    // 3. Выбор файла (САМОЕ ВАЖНОЕ СОБЫТИЕ)
    fileInput.addEventListener("change", (e) => {
        console.log("📁 СОБЫТИЕ CHANGE СРАБОТАЛО!");
        console.log("📁 Выбрано файлов:", fileInput.files.length);
        
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            console.log("📄 Имя файла:", file.name, "Размер:", file.size);
            processFile(file);
        } else {
            console.warn("⚠️ Файл не выбран (возможно, отмена в диалоге)");
        }
        
        // Сбрасываем значение, чтобы можно было выбрать тот же файл снова
        fileInput.value = ''; 
    });

    // Drag & Drop
    if (uploadCard) {
        uploadCard.addEventListener("dragover", (e) => { e.preventDefault(); uploadCard.classList.add("dragover"); });
        uploadCard.addEventListener("dragleave", (e) => { e.preventDefault(); uploadCard.classList.remove("dragover"); });
        uploadCard.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadCard.classList.remove("dragover");
            if (e.dataTransfer.files.length) {
                console.log("📂 Файл получен через Drag-Drop");
                processFile(e.dataTransfer.files[0]);
            }
        });
    }

    // --- ФУНКЦИЯ ЗАГРУЗКИ ---
    async function processFile(file) {
        console.log("⚙️ [processFile] Старт обработки");
        if (uploadStatus) uploadStatus.textContent = "📤 Загрузка...";

        try {
            // ✅ ИСПРАВЛЕНО: Убраны пробелы в конце URL!
            const API_URL = "https://friendly-halibut-rjpgrj4pvqq24g4-8000.app.github.dev";
            
            const formData = new FormData();
            formData.append("file", file);

            console.log("📡 Отправка запроса на:", API_URL + "/upload/");
            const response = await fetch(`${API_URL}/upload/`, { method: "POST", body: formData });
            
            console.log("📥 Ответ сервера:", response.status);
            if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

            const data = await response.json();
            console.log("✅ Данные получены:", data);

            sessionStorage.setItem("celma_file_id", data.file_id);
            sessionStorage.setItem("celma_analytics", JSON.stringify(data));

            if (uploadStatus) {
                uploadStatus.textContent = "✅ Готово! Переходим...";
                uploadStatus.style.color = "#2E7D32"; // Зеленый цвет успеха
            }

            // 🔥 НАДЕЖНЫЙ РЕДИРЕКТ (вставлено сюда)
            setTimeout(() => {
                console.log("⏰ Таймер истек. Выполняем переход...");
                
                try {
                    // Способ 1: replace (лучший вариант)
                    window.location.replace("processing.html");
                    
                    // Страховка: если через 100мс мы все еще на этой странице
                    setTimeout(() => {
                        if (window.location.href.indexOf("processing") === -1) {
                            console.log("⚠️ replace не сработал, пробуем href...");
                            window.location.href = "processing.html";
                        }
                    }, 100);
                } catch (e) {
                    console.error("❌ Ошибка редиректа:", e);
                    window.location.href = "processing.html";
                }
            }, 1000); // Ждем 1 секунду для надежности

        } catch (error) {
            console.error("💥 Ошибка:", error);
            if (uploadStatus) {
                uploadStatus.textContent = "❌ " + error.message;
                uploadStatus.style.color = "#d32f2f"; // Красный цвет ошибки
            }
        }
    }
});