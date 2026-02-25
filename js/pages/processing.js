// js/pages/processing.js
import { getProcessingStatus } from '../api.js';
import { getReportId } from '../storage.js';

document.addEventListener('DOMContentLoaded', async () => {
    const reportId = getReportId();
    if (!reportId) {
        // Если нет ID, возвращаем на главную
        window.location.href = 'index.html';
        return;
    }

    const progressBar = document.getElementById('progress-bar'); // предположим, есть элемент
    const statusText = document.getElementById('status-text');
    
    let completed = false;
    
    while (!completed) {
        try {
            const status = await getProcessingStatus(reportId);
            
            if (status.progress !== undefined && progressBar) {
                progressBar.style.width = status.progress + '%';
                progressBar.textContent = status.progress + '%';
            }
            
            if (status.status === 'completed') {
                completed = true;
                if (statusText) statusText.textContent = 'Анализ завершён!';
                // Переходим на дашборд
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 500);
                break;
            } else if (status.status === 'error') {
                throw new Error('Ошибка обработки');
            } else {
                if (statusText) statusText.textContent = `Обработка... ${status.progress}%`;
            }
            
            // Ждём 2 секунды перед следующим запросом
            await new Promise(resolve => setTimeout(resolve, 2000));
        } catch (error) {
            if (statusText) statusText.textContent = 'Ошибка: ' + error.message;
            break;
        }
    }
});