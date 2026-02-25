// js/api.js
const API_BASE_URL = 'http://localhost:8000'; // замените на реальный адрес бекенда

// Имитация задержки сети (для тестирования)
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export async function uploadReport(file) {
    // Реальный запрос (раскомментировать, когда бекенд готов)
    /*
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) throw new Error('Ошибка загрузки');
    return await response.json(); // ожидаем { report_id: "...", status: "processing" }
    */

    // Мок-версия для разработки
    console.log('Загружаем файл:', file.name);
    await delay(1500); // Имитация загрузки
    return { 
        report_id: 'report_123', 
        status: 'processing',
        message: 'Файл успешно загружен' 
    };
}

export async function getProcessingStatus(reportId) {
    // Реальный запрос
    /*
    const response = await fetch(`${API_BASE_URL}/process-status/${reportId}`);
    if (!response.ok) throw new Error('Ошибка получения статуса');
    return await response.json(); // { status: 'processing' | 'completed' | 'error', progress: 45 }
    */

    // Мок
    await delay(1000);
    // Симулируем прогресс
    const random = Math.random();
    if (random < 0.3) {
        return { status: 'processing', progress: 30 };
    } else if (random < 0.6) {
        return { status: 'processing', progress: 70 };
    } else {
        return { status: 'completed', progress: 100 };
    }
}

export async function getDashboardData(reportId) {
    // Реальный запрос
    /*
    const response = await fetch(`${API_BASE_URL}/dashboard/${reportId}`);
    if (!response.ok) throw new Error('Ошибка получения данных');
    return await response.json(); // Данные для дашборда
    */

    // Мок-данные для дашборда (можно расширить под ваши графики)
    await delay(800);
    return {
        kpi: {
            revenue: 1250000,
            expenses: 870000,
            profit: 380000,
            growth: 12.5
        },
        chartData: {
            labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
            actual: [1100000, 1150000, 1200000, 1180000, 1250000, 1300000],
            forecast: [1320000, 1350000, 1380000, 1400000, 1420000, 1450000]
        },
        anomalies: [
            { date: '2026-02-15', value: 95000, reason: 'Резкое падение выручки' }
        ],
        insights: [
            'Прогнозируется рост выручки на 8% в следующем квартале.',
            'Обнаружен кассовый разрыв в середине февраля — проверьте поступления.'
        ]
    };
}