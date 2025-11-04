document.addEventListener('DOMContentLoaded', function() {
    console.log('HH Parser frontend initialized');
    initializeApp();
});

function initializeApp() {
    initializeTooltips();
    initializeEventHandlers();
    initializeParserHandlers();
    loadStatistics();
}

function initializeParserHandlers() {
    // Обработчик для формы парсера
    const parseForm = document.getElementById('parseForm');
    if (parseForm) {
        parseForm.addEventListener('submit', handleParseFormSubmit);
        console.log('Parser form handler initialized');
    }
}

function handleParseFormSubmit(event) {
    event.preventDefault();
    console.log('Форма отправлена, начинаем парсинг...');

    const formData = new FormData(event.target);
    const jsonData = {
        'query': formData.get('query') || 'Python',
        'vacancy_count': parseInt(formData.get('vacancy_count') || 50),
        'keywords': formData.get('keywords') || '',
        'min_salary': formData.get('min_salary') || '',
        'experience': formData.get('experience') || '',
        'employment': formData.get('employment') || '',
        'min_experience_years': formData.get('min_experience_years') || ''
    };

    console.log('Данные для парсинга:', jsonData);
    startParsing(jsonData);
}

function startParsing(data) {
    const resultsDiv = document.getElementById('parseResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <h3>🔍 Парсим вакансии...</h3>
                <p>Это может занять несколько секунд</p>
            </div>
        `;
    }

    fetch('/parser/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Ответ сервера:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(handleParseResponse)
    .catch(error => {
        console.error('Ошибка парсинга:', error);
        showParseError('Ошибка сети при парсинге: ' + error.message);
    });
}

// static/parser/js/main.js - ЗАМЕНИТЕ эту функцию

function handleParseResponse(response) {
    console.log('Ответ от парсера:', response);
    const resultsDiv = document.getElementById('parseResults');
    if (!resultsDiv) return;

    if (response.success) {
        showParseSuccess(response);

        // АВТОМАТИЧЕСКОЕ ПЕРЕНАПРАВЛЕНИЕ НА ВАКАНСИИ
        if (response.saved > 0) {
            console.log('Автоматическое перенаправление через 3 секунды...');
            startCountdown(3, response.filter_url || '/vacancies/');
        }
    } else {
        showParseError(response.error || 'Неизвестная ошибка');
    }
}

function showParseSuccess(response) {
    const resultsDiv = document.getElementById('parseResults');

    let successHtml = `
        <div class="success">
            <h3>✅ Успешно завершено!</h3>
            <p>${response.message}</p>
            <div class="success-stats">
                <div class="stat">Найдено: ${response.found}</div>
                <div class="stat">Обработано: ${response.saved}</div>
            </div>
            <div class="success-actions">
    `;

    // Добавляем информацию о перенаправлении
    successHtml += `
                <div style="margin-bottom: 1rem; text-align: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
                    <p>⏳ <strong>Автоматическое перенаправление через <span id="countdown">3</span> секунд...</strong></p>
                    <small>Или нажмите кнопку ниже для немедленного перехода</small>
                </div>
    `;

    // Основные кнопки действий
    if (response.filter_url && response.found > 0) {
        successHtml += `
                <a href="${response.filter_url}" class="btn btn-success" style="text-decoration: none;">
                    🔍 Посмотреть найденные вакансии (${response.found})
                </a>
        `;
    } else {
        successHtml += `
                <a href="/vacancies/" class="btn btn-success" style="text-decoration: none;">
                    📋 Перейти к списку вакансий
                </a>
        `;
    }

    successHtml += `
                <a href="/parser/" class="btn btn-outline" style="text-decoration: none;">
                    🔄 Новый поиск
                </a>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = successHtml;

    // Запускаем обратный отсчет
    if (response.saved > 0) {
        startCountdown(3, response.filter_url || '/vacancies/');
    }
}

function startCountdown(seconds, redirectUrl) {
    let countdown = seconds;
    const countdownElement = document.getElementById('countdown');

    const countdownInterval = setInterval(function() {
        countdown--;
        if (countdownElement) {
            countdownElement.textContent = countdown;
        }

        if (countdown <= 0) {
            clearInterval(countdownInterval);
            console.log('Перенаправление на:', redirectUrl);
            window.location.href = redirectUrl;
        }
    }, 1000);
}
function showParseError(errorMessage) {
    const resultsDiv = document.getElementById('parseResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="error">
                <h3>❌ Ошибка!</h3>
                <p>${errorMessage}</p>
                <div class="success-actions">
                    <button onclick="resetParserForm()" class="btn btn-outline">
                        🔄 Попробовать снова
                    </button>
                </div>
            </div>
        `;
    }
}

function resetParserForm() {
    const form = document.getElementById('parseForm');
    if (form) {
        form.reset();
        // Устанавливаем значения по умолчанию
        document.getElementById('query').value = 'Python';
        document.getElementById('vacancy_count').value = '50';
    }
    const resultsDiv = document.getElementById('parseResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
    }
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Остальные существующие функции
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltipText = event.target.getAttribute('data-tooltip');
    if (!tooltipText) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    document.body.appendChild(tooltip);

    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

function initializeEventHandlers() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    initializeModals();
}

function handleSearch(event) {
    const searchValue = event.target.value.toLowerCase();
    const vacancyItems = document.querySelectorAll('.vacancy-item');
    vacancyItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchValue)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function initializeModals() {
    // Инициализация модальных окон
}

function loadStatistics() {
    fetch('/api/statistics/')
        .then(response => response.json())
        .then(data => {
            updateStatistics(data);
        })
        .catch(error => {
            console.log('Не удалось загрузить статистику:', error);
        });
}

function updateStatistics(data) {
    const statElements = document.querySelectorAll('[data-stat]');
    statElements.forEach(element => {
        const statKey = element.getAttribute('data-stat');
        if (data[statKey]) {
            element.textContent = data[statKey];
        }
    });

    // Обновляем статистику на странице парсера
    const recentVacancies = document.getElementById('recentVacancies');
    if (recentVacancies && data.recent_vacancies) {
        recentVacancies.textContent = data.recent_vacancies;
    }
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });
    return isValid;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Экспортируем функции для глобального использования
window.HHParser = {
    showNotification,
    validateForm,
    debounce,
    startParsing,
    handleParseResponse,
    resetParserForm,
    startCountdown
};