document.addEventListener("DOMContentLoaded", () => {
    console.log("📊 Инициализация дашборда...");

    const rawData = sessionStorage.getItem('celma_analytics');
    
    if (!rawData) {
        alert("⚠️ Данные не найдены! Загрузите файл заново.");
        window.location.href = 'addFile.html';
        return;
    }

    const data = JSON.parse(rawData);
    console.log("✅ Данные получены:", data);

    // 1. Заполняем KPI реальными числами
    document.getElementById('reportTitle').textContent = `Отчёт: ${data.filename || 'Без названия'}`;
    document.getElementById('kpiRows').textContent = data.rows || 0;
    document.getElementById('kpiCols').textContent = data.columns ? data.columns.length : 0;

    // 2. Строим график на основе РЕАЛЬНЫХ данных из ответа бэкенда
    buildRealChart(data);
    
    // 3. Генерируем инсайт на основе реальных цифр
    generateRealInsight(data);
});

function buildRealChart(data) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // Берем данные, которые прислал бэкенд
    const labels = data.chart_labels || [];
    const values = data.chart_data || [];
    const labelName = data.chart_label_name || 'Значения';

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: labelName,
                data: values,
                backgroundColor: 'rgba(46, 46, 46, 0.7)',
                borderColor: 'rgba(46, 46, 46, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: '#eee' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function generateRealInsight(data) {
    const summary = data.summary;
    let text = "Анализ завершен. ";

    if (summary && Object.keys(summary).length > 0) {
        const firstCol = Object.keys(summary)[0];
        const meanVal = Math.round(summary[firstCol].mean);
        const maxVal = Math.round(summary[firstCol].max);
        
        text += `Среднее значение по колонке "${firstCol}" составляет ${meanVal}. `;
        text += `Максимальное зафиксированное значение: ${maxVal}. `;
        
        if (maxVal > meanVal * 2) {
            text += "⚠️ Обнаружены значительные выбросы в данных.";
        } else {
            text += "Распределение данных выглядит стабильным.";
        }
    } else {
        text += "Числовые данные для глубокого анализа не найдены.";
    }

    document.getElementById('aiText').textContent = text;
}