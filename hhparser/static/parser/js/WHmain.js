// Глобальные переменные для хранения данных
let vacancies = [];
let filteredVacancies = [];
let generatedLetters = [];

// Показ сообщений
function showMessage(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Переключение вкладок
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Начало парсинга
async function startParsing() {
    const sourceUrl = document.getElementById('sourceUrl').value;
    const pagesCount = document.getElementById('pagesCount').value;
    
    if (!sourceUrl) {
        showMessage('errorMessage', 'УКАЖИТЕ ДАННЫЕ СЕРВИТОРА! "СКАНДИРОВАНИЕ БЕЗ ЦЕЛИ - ЕРЕСЬ!"');
        return;
    }
    
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('vacancyResults').innerHTML = '';

    try {
        // Имитация загрузки
        await new Promise(resolve => {
            let dots = 0;
            const interval = setInterval(() => {
                document.querySelector('#loadingIndicator p').textContent = 
                    'СКАНДИРУЕМ ДАННЫЕ' + '.'.repeat(dots % 4) + ' МОЛИТЕСЬ ОБ УСПЕХЕ';
                dots++;
            }, 300);
            
            setTimeout(() => {
                clearInterval(interval);
                resolve();
            }, 2000);
        });
        
        // Тестовые данные с тематикой Warhammer 40k
        vacancies = [
            {
                id: 1,
                title: "ТЕХНОЖРЕЦ (PYTHON РАЗРАБОТЧИК)",
                salary: "150 ДУКАТОВ (И ДОПОЛНИТЕЛЬНЫЕ ПОРЦИИ СВЯЩЕННОГО МАСЛА)",
                company: "АДЕПТУС МЕХАНИКУС (ФОРГЕВОРЛД ГРААХ)",
                description: "ИЩЕМ ОПЫТНОГО ТЕХНОЖРЕЦА (PYTHON РАЗРАБОТЧИКА) ДЛЯ ОБСЛУЖИВАНИЯ МАШИННОГО ДУХА. ТРЕБУЕТСЯ ЗНАНИЕ СВЯЩЕННЫХ БИБЛИОТЕК (DJANGO, FLASK). ОПЫТ ОЧИСТКИ ОТ ЕРЕСИ ПРИВЕТСТВУЕТСЯ.",
                experience: "1-3",
                employment: "full"
            },
            {
                id: 2,
                title: "ИНКВИЗИТОР DEVOPS",
                salary: "300-500 ДУКАТОВ (И ПРАВО НОСИТЬ РОЗУ ИНКВИЗИЦИИ)",
                company: "ОРДО ИНКВИЗИЦИИ (ОТДЕЛ HERETICUS)",
                description: "УДАЛЕННАЯ ПОЗИЦИЯ ДЛЯ ИНКВИЗИТОРА DEVOPS С ОПЫТОМ РАБОТЫ ОТ 3 ЛЕТ. ТРЕБУЕТСЯ ЗНАНИЕ СВЯЩЕННЫХ РИТУАЛОВ (DOCKER, KUBERNETES). ОБЯЗАТЕЛЬНО ОТСУТСТВИЕ СКЛОННОСТИ К ЕРЕСИ.",
                experience: "3-6",
                employment: "remote"
            },
            {
                id: 3,
                title: "КОМИССАР ПРОЕКТОВ",
                salary: "200 ДУКАТОВ (И ПРАВО НА ИСПОЛНИТЕЛЬНЫЕ РАССТРЕЛЫ)",
                company: "ИМПЕРИАЛЬНАЯ ГВАРДИЯ (ОТДЕЛ IT)",
                description: "НУЖЕН КОМИССАР (МЕНЕДЖЕР ПРОЕКТОВ), КОТОРЫЙ СМОЖЕТ ПОДДЕРЖАТЬ ДИСЦИПЛИНУ СРЕДИ РАЗРАБОТЧИКОВ. ОПЫТ ПОДАВЛЕНИЯ МЯТЕЖЕЙ ПРИВЕТСТВУЕТСЯ.",
                experience: "6+",
                employment: "full"
            }
        ];
        
        displayVacancies(vacancies);
        updateVacancySelect();
        showMessage('successMessage', `ОБНАРУЖЕНО ${vacancies.length} ВАКАНСИЙ! ИМПЕРАТОР БЛАГОСЛОВЛЯЕТ!`);
        
    } catch (error) {
        showMessage('errorMessage', `СКАНДИРОВАНИЕ ПРОВАЛЕНО: ${error.message.toUpperCase()}! ВОЗМОЖНА ЕРЕСЬ!`);
        console.error('Ошибка:', error);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
    }
}

// Отображение вакансий
function displayVacancies(vacs, containerId = 'vacancyResults') {
    const resultsContainer = document.getElementById(containerId);
    resultsContainer.innerHTML = '';
    
    if (vacs.length === 0) {
        resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center;">ВАКАНСИЙ НЕ ОБНАРУЖЕНО. ВОЗМОЖНО, ДАННЫЕ УНИЧТОЖЕНЫ ОРДО ИНКВИЗИЦИИ.</div>';
        return;
    }
    
    vacs.forEach(vacancy => {
        const card = document.createElement('div');
        card.className = 'vacancy-card';
        card.innerHTML = `
            <div class="vacancy-title">${vacancy.title}</div>
            <div class="vacancy-salary">${vacancy.salary || 'ДЕСЯТИНА НЕ УКАЗАНА (ВОЗМОЖНО, ОПЛАТА ЧЕСТЬЮ СЛУЖЕНИЯ)'}</div>
            <div class="vacancy-company">${vacancy.company}</div>
            <div>${vacancy.description}</div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                ОПЫТ: ${getExperienceText(vacancy.experience)} | 
                ФОРМА: ${getEmploymentText(vacancy.employment)}
            </div>
        `;
        resultsContainer.appendChild(card);
    });
}

// Обновление select с вакансиями
function updateVacancySelect() {
    const select = document.getElementById('selectedVacancy');
    select.innerHTML = '<option value="">-- ИЗБЕРИТЕ ВАКАНСИЮ --</option>';
    
    vacancies.forEach(vac => {
        const option = document.createElement('option');
        option.value = vac.id;
        option.textContent = `${vac.title} (${vac.company})`;
        select.appendChild(option);
    });
}

// Применение фильтров
function applyFilters() {
    const keywords = document.getElementById('keywords').value.toLowerCase();
    const minSalary = document.getElementById('minSalary').value;
    const experience = document.getElementById('experience').value;
    const employment = document.getElementById('employment').value;
    
    filteredVacancies = vacancies.filter(vac => {
        if (keywords && 
            !vac.title.toLowerCase().includes(keywords) && 
            !vac.description.toLowerCase().includes(keywords) && 
            !vac.company.toLowerCase().includes(keywords)) {
            return false;
        }
        
        if (minSalary) {
            const salaryNum = parseInt(vac.salary.replace(/\D/g,''));
            if (isNaN(salaryNum)) return false;
            if (salaryNum < parseInt(minSalary)) return false;
        }
        
        if (experience && vac.experience !== experience) {
            return false;
        }
        
        if (employment && vac.employment !== employment) {
            return false;
        }
        
        return true;
    });
    
    displayVacancies(filteredVacancies, 'filterResults');
    
    if (filteredVacancies.length === 0) {
        showMessage('errorMessage', 'ВАКАНСИЙ НЕ ОБНАРУЖЕНО. ВОЗМОЖНО, ТРЕБУЕТСЯ ЭКСТЕРМИНАТУС.');
    } else {
        showMessage('successMessage', `ОБНАРУЖЕНО ${filteredVacancies.length} ВАКАНСИЙ! ПУРГАЦИЯ УСПЕШНА!`);
    }
}

// Генерация письма
function generateLetter() {
    const vacancyId = document.getElementById('selectedVacancy').value;
    const template = document.getElementById('letterTemplate').value;
    const customText = document.getElementById('customText').value;
    
    if (!vacancyId) {
        showMessage('errorMessage', 'ИЗБЕРИТЕ ВАКАНСИЮ! "НЕРЕШИТЕЛЬНОСТЬ - ПУТЬ К ЕРЕСИ!"');
        return;
    }
    
    const vacancy = vacancies.find(v => v.id == vacancyId);
    let letter = '';
    
    switch(template) {
        case 'support':
            letter = `ВЕЛИКОМУ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я, СМИРЕННЫЙ СЛУГА ИМПЕРИУМА, ПИШУ ПО ПОВОДУ ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ СЛУЖЕНИЯ С ${vacancy.description.split(' ').slice(0, 3).join(' ').toUpperCase()}...\n\n` +
                     `КАК ИСТИННЫЙ АДЕПТУС МЕХАНИКУС, Я ТЩАТЕЛЕН В ОБСЛУЖИВАНИИ МАШИННОГО ДУХА И НЕПОДКУПЕН.\n\n` +
                     `С ВЕРНОСТЬЮ ИМПЕРАТОРУ,\nВАШ ПОСЛУШНИК`;
            break;
            
        case 'devops':
            letter = `ВЕЛИКОМУ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ЗАИНТЕРЕСОВАН В ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ СЛУЖЕНИЯ В DEVOPS СОСТАВЛЯЕТ 4 ГОДА (ЭТО КАК 4 КРЕСТОВЫХ ПОХОДА БЕЗ ОТПУСКА).\n\n` +
                     `КАК ИСТИННЫЙ ТЕХНОЖРЕЦ, Я МОГУ УСМИРИТЬ ДАЖЕ САМОГО СТРОПТИВОГО МАШИННОГО ДУХА.\n\n` +
                     `С ВЕРНОСТЬЮ ИМПЕРАТОРУ`;
            break;
            
        default:
            letter = `ВЕЛИКОМУ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ПИШУ ПО ПОВОДУ ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ И НАВЫКИ СООТВЕТСТВУЮТ ВАШИМ ТРЕБОВАНИЯМ (ИЛИ Я НАУЧУСЬ, КАК НОВОБРАНЕЦ АДЕПТУС АСТАРТЕС).\n\n` +
                     `С ВЕРНОСТЬЮ ИМПЕРАТОРУ`;
    }
    
    if (customText) {
        letter += '\n\nP.S. ' + customText.toUpperCase();
    }
    
    const letterContainer = document.getElementById('generatedLetter');
    letterContainer.innerHTML = letter.replace(/\n/g, '<br>');
    document.getElementById('letterResult').style.display = 'block';
    
    generatedLetters.push({
        vacancyId: vacancy.id,
        text: letter,
        date: new Date()
    });
    
    showMessage('successMessage', 'МОЛИТВОПИСЬ СОЗДАНА! ГОТОВА К ОТПРАВКЕ АСТРОПАТОМ!');
}

// Сохранение письма
function saveLetter() {
    showMessage('successMessage', 'МОЛИТВОПИСЬ ВНЕСЕНА В КОДЕКС!');
    
    const btn = event.target;
    btn.textContent = 'ВНЕСЕНО! (ОЖИДАЕТ ОДОБРЕНИЯ)';
    btn.style.backgroundColor = '#1a472a';
    setTimeout(() => {
        btn.textContent = 'ВНЕСТИ В КОДЕКС';
        btn.style.backgroundColor = '';
    }, 2000);
}

// Экспорт данных
function exportData() {
    const exportType = document.getElementById('exportType').value;
    const exportContent = document.getElementById('exportContent').value;
    
    let data = '';
    
    if (exportContent === 'vacancies' || exportContent === 'all') {
        data += 'ВАКАНСИИ:\n\n';
        vacancies.forEach(vac => {
            data += `ДОЛЖНОСТЬ: ${vac.title}\n`;
            data += `ОРГАНИЗАЦИЯ: ${vac.company}\n`;
            data += `ДЕСЯТИНА: ${vac.salary || 'НЕ УКАЗАНА'}\n`;
            data += `ОПИСАНИЕ: ${vac.description}\n\n`;
        });
    }
    
    if (exportContent === 'letters' || exportContent === 'all') {
        data += '\nМОЛИТВОПИСИ:\n\n';
        generatedLetters.forEach((letter, idx) => {
            const vac = vacancies.find(v => v.id == letter.vacancyId);
            data += `МОЛИТВОПИСЬ #${idx + 1} (${vac.title})\n`;
            data += `${letter.text}\n\n`;
        });
    }
    
    alert(`АРХИВАЦИЯ В ${getExportTypeText(exportType)}!\n\n${data}`);
    showMessage('successMessage', `АРХИВАЦИЯ В ${getExportTypeText(exportType)} ЗАВЕРШЕНА! ИМПЕРАТОР ГОРДИТСЯ ВАМИ!`);
}

// Вспомогательные функции
function getExperienceText(code) {
    const experiences = {
        'no': 'НЕОФИТ (КАК НОВОБРАНЕЦ АДЕПТУС АСТАРТЕС)',
        '1-3': '1-3 ГОДА (КАК ОПЫТНЫЙ ГВАРДИЕЦ)',
        '3-6': '3-6 ЛЕТ (КАК ВЕТЕРАН КАДИИ)',
        '6+': 'БОЛЕЕ 6 ЛЕТ (КАК СЕРЫЙ РЫЦАРЬ)'
    };
    return experiences[code] || 'НЕИЗВЕСТНО (ВОЗМОЖНО, ЕРЕТИЧЕСКИЙ ОПЫТ)';
}

function getEmploymentText(code) {
    const employments = {
        'full': 'ПОЛНАЯ (КАК У АДЕПТУС МЕХАНИКУС)',
        'part': 'ЧАСТИЧНАЯ (КАК У МИЛИТАРУМ ТЕМПЕСТУС)',
        'remote': 'ДИСТАНЦИОННАЯ (КАК У АСТРОПАТА)',
        'project': 'КРЕСТОВЫЙ ПОХОД (ПРОЕКТНАЯ)'
    };
    return employments[code] || 'НЕИЗВЕСТНО (ВОЗМОЖНО, ЕРЕТИЧЕСКАЯ)';
}

function getExportTypeText(type) {
    const types = {
        'docx': 'КЕРБЕР (DOCX)',
        'pdf': 'СВЯЩЕННЫЙ СВИТОК (PDF)',
        'txt': 'ДОКСОГРАФИЯ (TXT)',
        'csv': 'ТАБУЛЯРУМ (CSV)',
        'xlsx': 'КОДЕКС (XLSX)'
    };
    return types[type] || type.toUpperCase();
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    // Эффект загрузки Warhammer
    setTimeout(() => {
        document.querySelector('h1').style.textShadow = '0 0 15px #ff0000';
        setTimeout(() => {
            document.querySelector('h1').style.textShadow = '0 0 10px #5e0000';
        }, 500);
    }, 500);
});