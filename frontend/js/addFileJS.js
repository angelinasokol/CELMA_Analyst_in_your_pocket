// ✅ 1. URL БЕЗ пробелов в конце!
const API_URL = "https://friendly-halibut-rjpgrj4pvqq24g4-8000.app.github.dev";

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Скрипт загружен, начинаем инициализацию...");

    // 🔥 2. ЖЕСТКАЯ БЛОКИРОВКА ВСЕХ ФОРМ НА СТРАНИЦЕ
    // Это предотвращает перезагрузку страницы при клике
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log("🚫 Форма заблокирована (preventDefault)");
            return false;
        });
        form.setAttribute('onsubmit', 'return false;');
    });

    const uploadCard = document.querySelector(".upload-card");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");

    if (!uploadCard || !fileInput) {
        console.error("❌ ОШИБКА: Не найдены элементы uploadCard или fileInput в HTML");
        return;
    }

    // --- Обработчик клика по карточке ---
    uploadCard.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log("👆 Клик по карточке, открываем выбор файла");
        fileInput.click();
    });

    // --- Обработчик выбора файла через input ---
    fileInput.addEventListener("change", (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log("📁 Файл выбран через input:", fileInput.files[0]?.name);
        
        if (fileInput.files.length > 0) {
            processFile(fileInput.files[0]);
        } else {
            console.warn("⚠️ Файл не выбран");
        }
    });

    // --- Drag & Drop: Наведение ---
    uploadCard.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadCard.classList.add("dragover");
        console.log("📂 Drag over (наведение)");
    });

    // --- Drag & Drop: Уход ---
    uploadCard.addEventListener("dragleave", (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadCard.classList.remove("dragover");
        console.log("📂 Drag leave (уход)");
    });

    // --- Drag & Drop: Сброс файла ---
    uploadCard.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadCard.classList.remove("dragover");
        
        console.log("📂 Drop event (сброс)");
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            console.log("✅ Файл получен через Drag-Drop:", files[0].name);
            processFile(files[0]);
        } else {
            console.warn("⚠️ В drop нет файлов");
        }
    });

    // ==========================================
    // ОСНОВНАЯ ФУНКЦИЯ ОБРАБОТКИ
    // ==========================================
    async function processFile(file) {
        console.log("🚀 [processFile] Запуск обработки файла:", file.name);
        
        // 1. Проверка размера (макс 10 МБ)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            const msg = "❌ Файл слишком большой (>10 МБ)";
            console.error(msg);
            uploadStatus.textContent = msg;
            return;
        }
        
        // 2. Проверка расширения
        const ext = file.name.split(".").pop().toLowerCase();
        const allowed = ["csv", "xlsx", "xml"];
        
        if (!allowed.includes(ext)) {
            const msg = "❌ Недопустимый формат (разрешены: .csv, .xlsx, .xml)";
            console.error(msg);
            uploadStatus.textContent = msg;
            return;
        }

        console.log("✅ Проверки пройдены. Начинаем загрузку...");
        uploadStatus.textContent = "📤 Загружаем файл на сервер...";
        
        try {
            // Подготовка данных
            const formData = new FormData();
            formData.append("file", file);
            
            const targetUrl = `${API_URL}/upload/`;
            console.log("📡 Отправка POST запроса на:", targetUrl);
            
            // ЗАПРОС К СЕРВЕРУ
            const response = await fetch(targetUrl, {
                method: "POST",
                body: formData
                // Заголовки Content-Type ставить не нужно, браузер сам ставит multipart/form-data
            });
            
            console.log("📥 Получен ответ от сервера. Статус:", response.status, "OK:", response.ok);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Ошибка сервера ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            console.log("✅ Успех! Данные от сервера:", result);
            
            // Сохранение ID файла
            const fileId = result.file_id;
            if (!fileId) {
                throw new Error("Сервер не вернул file_id");
            }

            uploadStatus.textContent = "📊 Анализ данных...";
            
            // Сохраняем в sessionStorage для следующей страницы
            sessionStorage.setItem('celma_file_id', fileId);
            sessionStorage.setItem('celma_analytics', JSON.stringify(result));
            console.log("💾 Данные сохранены в sessionStorage");
            
            // ==========================================
            // РЕДИРЕКТ
            // ==========================================
            uploadStatus.textContent = "✅ Готово! Перенаправляем...";
            
            console.log("⏳ Таймер редиректа запущен (500 мс)...");
            
            setTimeout(() => {
                console.log("⏰ Таймер сработал. Текущий URL:", window.location.href);
                console.log("🔄 Выполняем переход на processing.html");
                
                // Используем replace, чтобы нельзя было вернуться кнопкой "Назад" на эту же страницу с файлом
                window.location.replace("processing.html");
                
                // Если replace не сработает (редко), пробуем href
                // window.location.href = "processing.html"; 
            }, 500);
            
        } catch (error) {
            console.error("💥 КРИТИЧЕСКАЯ ОШИБКА в processFile:", error);
            console.error("Stack trace:", error.stack);
            
            let errorMsg = "❌ Произошла неизвестная ошибка";
            if (error.message) {
                errorMsg = "❌ " + error.message;
            }
            // Если ошибка сетевая (Failed to fetch)
            if (error.message.includes("Failed to fetch") || error.message.includes("fetch")) {
                errorMsg = "❌ Нет связи с сервером. Проверьте консоль и подключение.";
            }
            
            uploadStatus.textContent = errorMsg;
        }
    }
});