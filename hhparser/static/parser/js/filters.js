// Функции для работы с фильтрами
function toggleFilters() {
    const container = document.getElementById('filtersFormContainer');
    if (container) {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    }
}

function resetFilters() {
    const form = document.getElementById('parseForm');
    if (form) {
        // Сбрасываем только поля фильтров
        document.getElementById('keywords').value = '';
        document.getElementById('min_salary').value = '';
        document.getElementById('experience').value = '';
        document.getElementById('employment').value = '';
        document.getElementById('min_experience_years').value = '';
    }
}

function hideFilterResults() {
    const resultsDiv = document.getElementById('filterResults');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

// Показываем фильтры если есть параметры в URL
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('keywords') || urlParams.has('min_salary') ||
        urlParams.has('experience') || urlParams.has('employment') ||
        urlParams.has('min_experience_years')) {

        // Автоматически применяем фильтры
        setTimeout(() => {
            if (window.filtersManager) {
                window.filtersManager.applyFilters();
            }
        }, 500);
    }
});