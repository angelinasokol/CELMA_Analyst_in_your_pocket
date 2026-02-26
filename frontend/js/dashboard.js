 const salesChart = new Chart(
        document.getElementById('salesChart'),
        {
            type: 'line',
            data: {
                labels: ['Сен', 'Окт', 'Ноя', 'Дек', 'Янв'],
                datasets: [{
                    label: 'Продажи',
                    data: [2400000, 2600000, 2800000, 3000000, 3240000],
                    borderColor: '#2E2E2E',
                    backgroundColor: 'rgba(46,46,46,0.1)',
                    fill: true,
                    tension: 0.3
                }]
            }
        }
    );

    const forecastChart = new Chart(
        document.getElementById('forecastChart'),
        {
            type: 'bar',
            data: {
                labels: ['Фев', 'Мар', 'Апр'],
                datasets: [{
                    label: 'Прогноз',
                    data: [3600000, 3900000, 4200000],
                    backgroundColor: '#2E2E2E'
                }]
            }
        }
    );