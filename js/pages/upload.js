// js/pages/upload.js
import { uploadReport } from '../api.js';
import { saveReportId } from '../storage.js';

document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form'); // предположим, у вас есть форма
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const statusDiv = document.getElementById('upload-status');

    if (!uploadForm) return; // если не на странице загрузки

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showStatus('Выберите файл', 'error');
            return;
        }

        // Блокируем кнопку и показываем загрузку
        uploadButton.disabled = true;
        showStatus('Загрузка...', 'info');

        try {
            const result = await uploadReport(file);
            saveReportId(result.report_id);
            showStatus('Файл загружен! Перенаправление...', 'success');
            
            // Переход на страницу обработки
            setTimeout(() => {
                window.location.href = 'processing.html';
            }, 1000);
        } catch (error) {
            showStatus('Ошибка: ' + error.message, 'error');
            uploadButton.disabled = false;
        }
    });

    function showStatus(message, type) {
        if (statusDiv) {
            statusDiv.textContent = message;
            statusDiv.className = `status-${type}`; // можно стилизовать
        }
    }
});