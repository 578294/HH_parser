// static/parser/js/filters.js

// Функции для работы с фильтрами на главной странице
function toggleFilters() {
    const container = document.getElementById('filtersFormContainer');
    if (container) {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    }
}

function resetFilters() {
    const form = document.getElementById('filterForm');
    if (form) {
        form.reset();
    }
    const resultsDiv = document.getElementById('filterResults');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
    if (window.filtersManager) {
        window.filtersManager.saveFilters({});
    }
}

function hideFilterResults() {
    const resultsDiv = document.getElementById('filterResults');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

// Функция отображения отфильтрованных вакансий
function displayFilteredVacancies(vacancies, style) {
    const resultsContent = document.getElementById('filterResultsContent');
    const resultsTitle = document.getElementById('filterResultsTitle');

    if (!resultsContent || !resultsTitle) return;

    // Устанавливаем заголовок
    let title = '';
    switch(style) {
        case 'HP':
            title = `🧙‍♂️ Найдено заклинаний: ${vacancies.length}`;
            break;
        case 'SP':
            title = `🎭 Найдено вакансий: ${vacancies.length}`;
            break;
        case 'WH':
            title = `⚔️ Обнаружено записей: ${vacancies.length}`;
            break;
        default:
            title = `🔍 Найдено вакансий: ${vacancies.length}`;
    }
    resultsTitle.textContent = title;

    if (vacancies.length === 0) {
        let noResultsMessage = '';
        switch(style) {
            case 'HP':
                noResultsMessage = '🧙‍♂️ Ничего не найдено! Возможно, вакансии скрыты мантией-невидимкой...';
                break;
            case 'SP':
                noResultsMessage = '😞 Ничего не найдено! Серьезно, совсем ничего!';
                break;
            case 'WH':
                noResultsMessage = '💀 Ничего не найдено! Возможно, требуется экстерминатус.';
                break;
            default:
                noResultsMessage = '🔍 По вашему запросу ничего не найдено.';
        }
        resultsContent.innerHTML = `<div class="no-results">${noResultsMessage}</div>`;
        return;
    }

    let html = '<div class="vacancies-grid">';

    vacancies.forEach(vacancy => {
        const description = vacancy.description ?
            vacancy.description.substring(0, 100) + '...' : '';

        html += `
            <div class="vacancy-card filtered">
                <div class="vacancy-header">
                    <h4 class="vacancy-title">${escapeHtml(vacancy.title)}</h4>
                    <span class="vacancy-salary">${escapeHtml(vacancy.salary)}</span>
                </div>
                <div class="vacancy-company">${escapeHtml(vacancy.company)}</div>
                <div class="vacancy-meta">
                    <span class="experience">${escapeHtml(vacancy.experience)}</span>
                    <span class="employment">${escapeHtml(vacancy.employment)}</span>
                </div>
                ${description ? `<div class="vacancy-description">${escapeHtml(description)}</div>` : ''}
                <div class="vacancy-actions">
                    <a href="${vacancy.link}" target="_blank" class="btn btn-small">
                        🔗 Открыть
                    </a>
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsContent.innerHTML = html;
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Показываем фильтры если есть параметры в URL
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('keywords') || urlParams.has('min_salary') ||
        urlParams.has('experience') || urlParams.has('employment')) {
        toggleFilters();

        // Автоматически применяем фильтры
        setTimeout(() => {
            if (window.filtersManager) {
                window.filtersManager.applyFilters();
            }
        }, 500);
    }
});