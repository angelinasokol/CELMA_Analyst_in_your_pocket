document.addEventListener("DOMContentLoaded", () => {
    const rawData = sessionStorage.getItem('celma_analytics');
    
    if (!rawData) {
        alert("⚠️ Данные не найдены! Загрузите файл заново.");
        window.location.href = 'addFile.html';
        return;
    }

    const data = JSON.parse(rawData);
    console.log("🤖 ML Данные получены:", data);

    // 1. Заполняем KPI реальными ML-метриками
    document.getElementById('reportTitle').textContent = `Отчёт: ${data.filename || 'Анализ'}`;
    document.getElementById('kpiRows').textContent = data.rows;
    document.getElementById('kpiCols').textContent = data.columns.length;
    
    // Обновляем карточки KPI (предполагаем, что их 3 штуки в HTML)
    const kpiValues = document.querySelectorAll('.kpi-value');
    const kpiDescs = document.querySelectorAll('.kpi-desc');
    
    if(kpiValues.length >= 3 && kpiDescs.length >= 3) {
        kpiValues[0].textContent = data.rows; // Строки
        kpiDescs[0].textContent = "Записей в отчете";
        
        kpiValues[1].textContent = data.target_metric ? data.target_metric.substring(0, 15) + "..." : "Метрика"; // Название метрики (обрезаем если длинное)
        kpiDescs[1].textContent = "Целевой показатель";
        
        // Прогноз
        const forecastVal = Math.round(data.summary?.forecast_next_month || 0);
        kpiValues[2].textContent = forecastVal.toLocaleString('ru-RU'); 
        kpiDescs[2].textContent = "Прогноз на след. период";
    }

    // 2. Строим ПРОФЕССИОНАЛЬНЫЙ график (История + Прогноз)
    buildMLChart(data);
    
    // 3. Выводим настоящий AI-инсайт
    document.getElementById('aiText').textContent = data.ai_insight || "Анализ завершен.";
});

function buildMLChart(data) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    // История
    const labelsHistory = data.chart_history_labels || [];
    const dataHistory = data.chart_history_data || [];
    
    // Прогноз
    const labelsForecast = data.chart_forecast_labels || [];
    const dataForecast = data.chart_forecast_data || [];

    // Создаем единую ось X
    const allLabels = [...labelsHistory, ...labelsForecast];
    
    // Набор данных 1: История (Столбцы)
    const datasetHistory = {
        label: 'Факт (История)',
        data: [...dataHistory, ...Array(labelsForecast.length).fill(null)], // null разрывает линию
        type: 'bar',
        backgroundColor: 'rgba(46, 46, 46, 0.8)',
        borderRadius: 4,
        order: 2
    };

    // Набор данных 2: Прогноз (Линия)
    const datasetForecast = {
        label: 'ML Прогноз',
        data: [...Array(labelsHistory.length).fill(null), ...dataForecast], // сдвиг вправо
        type: 'line',
        borderColor: '#d32f2f', // Красный цвет
        backgroundColor: 'rgba(211, 47, 47, 0.2)',
        borderWidth: 3,
        borderDash: [5, 5], // Пунктирная линия
        pointRadius: 4,
        pointBackgroundColor: '#fff',
        fill: false,
        tension: 0.3, // Плавность линии
        order: 1
    };

    new Chart(ctx, {
        data: {  // <-- ВОТ ЭТОГО НЕ ХВАТАЛО! Ключ data:
            labels: allLabels,
            datasets: [datasetHistory, datasetForecast]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: { 
                    beginAtZero: true, 
                    grid: { color: '#eee' },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('ru-RU');
                        }
                    }
                },
                x: { grid: { display: false } }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y).toLocaleString('ru-RU');
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
}