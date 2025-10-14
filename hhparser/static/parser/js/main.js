// Tab switching functionality
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabId).classList.add('active');
    
    // Make selected tab active
    event.currentTarget.classList.add('active');
}

// Show/hide style menu
function showStyleMenu() {
    const menu = document.getElementById('styleMenu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

// Change page style
function changeStyle(style) {
    if (style === 'SP') {
        window.location.href = 'http://127.0.0.1:8000/SPindex/';
    } else if (style === 'HP') {
        window.location.href = 'http://127.0.0.1:8000/HPindex/';
    } else if (style === 'WH') {
        window.location.href = 'http://127.0.0.1:8000/WHindex/';
    }
    document.getElementById('styleMenu').style.display = 'none';
}

// Show status messages
function showMessage(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Parsing functionality
async function startParsing() {
    const sourceUrl = document.getElementById('sourceUrl').value;
    const pagesCount = document.getElementById('pagesCount').value;
    
    if (!sourceUrl) {
        showMessage('errorMessage', 'Пожалуйста, укажите URL для парсинга');
        return;
    }
    
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('vacancyResults').innerHTML = '';

    try {
        // Here would be a real backend request
        // This is a mock for demonstration
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Example results
        const mockResults = [
            {
                title: "Python разработчик",
                salary: "от 150 000 руб.",
                company: "ООО ТехноЛаб",
                description: "Ищем опытного Python разработчика для работы над высоконагруженным проектом."
            },
            {
                title: "Django backend developer",
                salary: "$3000 - $5000",
                company: "International Tech Corp",
                description: "Remote position for Django expert with 3+ years experience."
            }
        ];
        
        displayVacancies(mockResults);
        showMessage('successMessage', 'Парсинг завершен успешно! Найдено ' + mockResults.length + ' вакансий');
    } catch (error) {
        showMessage('errorMessage', 'Ошибка при парсинге: ' + error.message);
        console.error('Ошибка:', error);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
    }
}

// Display vacancies
function displayVacancies(vacancies) {
    const resultsContainer = document.getElementById('vacancyResults');
    resultsContainer.innerHTML = '';
    
    vacancies.forEach(vacancy => {
        const card = document.createElement('div');
        card.className = 'vacancy-card';
        card.innerHTML = `
            <div class="vacancy-title">${vacancy.title}</div>
            <div class="vacancy-salary">${vacancy.salary || 'Зарплата не указана'}</div>
            <div class="vacancy-company">${vacancy.company}</div>
            <div>${vacancy.description}</div>
        `;
        resultsContainer.appendChild(card);
    });
}

// Apply filters
function applyFilters() {
    // Here would be filtering implementation
    showMessage('successMessage', 'Фильтры применены');
}

// Generate cover letter
function generateLetter() {
    // Here would be letter generation via DeepSeek API
    const letterContainer = document.getElementById('generatedLetter');
    letterContainer.innerHTML = `
        <p>Уважаемые коллеги,</p>
        <p>Я заинтересовался вакансией на позицию Python разработчика и хотел бы подать свою кандидатуру.</p>
        <p>Мой опыт работы с Django составляет 4 года, и я уверен, что могу внести значительный вклад в ваш проект.</p>
        <p>С уважением,<br>[Ваше имя]</p>
    `;
    document.getElementById('letterResult').style.display = 'block';
    showMessage('successMessage', 'Письмо успешно сгенерировано');
}

// Save letter
function saveLetter() {
    // Here would be letter saving implementation
    showMessage('successMessage', 'Письмо сохранено');
}

// Export data
function exportData() {
    // Here would be data export implementation
    showMessage('successMessage', 'Данные успешно экспортированы');
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code can go here
});