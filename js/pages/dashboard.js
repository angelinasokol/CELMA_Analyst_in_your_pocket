// js/pages/dashboard.js
import { getDashboardData } from '../api.js';
import { getReportId } from '../storage.js';

document.addEventListener('DOMContentLoaded', async () => {
    const reportId = getReportId();
    if (!reportId) {
        window.location.href = 'index.html';
        return;
    }

    const loadingDiv = document.getElementById('dashboard-loading');
    const contentDiv = document.getElementById('dashboard-content');

    try {
        // Показываем загрузку
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (contentDiv) contentDiv.style.display = 'none';

        const data = await getDashboardData(reportId);

        // Заполняем KPI
        document.getElementById('revenue-value').textContent = formatMoney(data.kpi.revenue);
        document.getElementById('expenses-value').textContent = formatMoney(data.kpi.expenses);
        document.getElementById('profit-value').textContent = formatMoney(data.kpi.profit);
        document.getElementById('growth-value').textContent = data.kpi.growth + '%';

        // Здесь можно вызвать функцию для отрисовки графиков (используя Chart.js или подобное)
        renderChart(data.chartData);

        // Выводим инсайты
        const insightsList = document.getElementById('insights-list');
        if (insightsList) {
            insightsList.innerHTML = data.insights.map(text => `<li>${text}</li>`).join('');
        }

        // Скрываем загрузку, показываем контент
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (contentDiv) contentDiv.style.display = 'block';

    } catch (error) {
        if (loadingDiv) loadingDiv.textContent = 'Ошибка загрузки данных: ' + error.message;
    }
});

function formatMoney(amount) {
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(amount);
}

function renderChart(chartData) {
    // Здесь код для Chart.js, если он у вас подключён
    // Пример:
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { label: 'Факт', data: chartData.actual, borderColor: 'blue' },
                { label: 'Прогноз', data: chartData.forecast, borderColor: 'green', borderDash: [5,5] }
            ]
        }
    });
}