document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DEBUG MODE ===');
    console.log('Проверка доступности API:');

    // Проверяем основные endpoints
    const endpoints = [
        '/api/statistics/',
        '/api/vacancies/',
        '/vacancies/'
    ];

    endpoints.forEach(endpoint => {
        fetch(endpoint)
            .then(response => {
                console.log(`✅ ${endpoint}: ${response.status}`);
                if (response.ok) {
                    return response.json().then(data => {
                        console.log(`📊 ${endpoint} данные:`, data);
                    });
                }
            })
            .catch(error => {
                console.error(`❌ ${endpoint}: ${error}`);
            });
    });

    // Проверяем глобальные функции
    console.log('Глобальные функции:');
    console.log('- startParsing:', typeof startParsing);
    console.log('- handleParseResponse:', typeof handleParseResponse);
    console.log('- HHParser:', window.HHParser);

    // Проверяем наличие элементов
    console.log('Критические элементы:');
    console.log('- parseForm:', document.getElementById('parseForm'));
    console.log('- parseResults:', document.getElementById('parseResults'));

    // Проверяем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    console.log('- CSRF токен:', csrfToken ? 'найден' : 'не найден');
});