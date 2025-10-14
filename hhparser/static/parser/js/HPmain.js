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
        showMessage('errorMessage', 'УКАЖИТЕ СВИТОК С ВАКАНСИЯМИ! "ACCIO" НЕ СРАБОТАЕТ БЕЗ ЦЕЛИ!');
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
                    'ИЩЕМ ВАКАНСИИ В ЗЕРКАЛЕ ЕИНАЛЕЖ' + '.'.repeat(dots % 4);
                dots++;
            }, 300);
            
            setTimeout(() => {
                clearInterval(interval);
                resolve();
            }, 2000);
        });
        
        // Тестовые данные с тематикой Гарри Поттера
        vacancies = [
            {
                id: 1,
                title: "МАСТЕР ЗЕЛИЙ (PYTHON РАЗРАБОТЧИК)",
                salary: "150 ГАЛЕОНОВ (ПЛЮС БОНУСЫ В ВИДЕ FELIX FELICIS)",
                company: "АПТЕКА 'СКОЛЬЗКИЙ ГОРШОК'",
                description: "ИЩЕМ ОПЫТНОГО ЗЕЛЬЕВАРА (PYTHON РАЗРАБОТЧИКА) ДЛЯ СОЗДАНИЯ ВЫСОКОКАЧЕСТВЕННЫХ ЗЕЛИЙ (КОДА). ТРЕБУЕТСЯ ЗНАНИЕ МАГИЧЕСКИХ БИБЛИОТЕК (DJANGO, FLASK).",
                experience: "1-3",
                employment: "full"
            },
            {
                id: 2,
                title: "ВОЛШЕБНИК DEVOPS",
                salary: "300-500 ГАЛЕОНОВ (ЗАВИСИТ ОТ УМЕНИЯ ПРИРУЧИТЬ ГИППОГРИФА)",
                company: "МИНИСТЕРСТВО МАГИИ (IT ОТДЕЛ)",
                description: "УДАЛЕННАЯ ПОЗИЦИЯ ДЛЯ ВОЛШЕБНИКА DEVOPS С ОПЫТОМ РАБОТЫ ОТ 3 ЛЕТ. ТРЕБУЕТСЯ ЗНАНИЕ ЗАКЛИНАНИЙ (DOCKER, KUBERNETES).",
                experience: "3-6",
                employment: "remote"
            },
            {
                id: 3,
                title: "УЧИТЕЛЬ ЗАЩИТЫ ОТ ТЕМНЫХ ИСКУССТВ (МЕНЕДЖЕР ПРОЕКТОВ)",
                salary: "200 ГАЛЕОНОВ (И ГАРАНТИЯ РАБОТЫ НА ВЕСЬ УЧЕБНЫЙ ГОД)",
                company: "ХОГВАРТС",
                description: "НУЖЕН ПРЕПОДАВАТЕЛЬ (МЕНЕДЖЕР ПРОЕКТОВ), КОТОРЫЙ СМОЖЕТ СПРАВИТЬСЯ С НЕПОСЛУШНЫМИ СТУДЕНТАМИ (РАЗРАБОТЧИКАМИ).",
                experience: "6+",
                employment: "full"
            }
        ];
        
        displayVacancies(vacancies);
        updateVacancySelect();
        showMessage('successMessage', `НАЙДЕНО ${vacancies.length} ВАКАНСИЙ! "ACCIO" СРАБОТАЛО!`);
        
    } catch (error) {
        showMessage('errorMessage', `ЗАКЛИНАНИЕ НЕ СРАБОТАЛО: ${error.message.toUpperCase()}!`);
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
        resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center;">НИЧЕГО НЕ НАЙДЕНО! ВОЗМОЖНО, ВАКАНСИИ СКРЫТЫ МАНТИЕЙ-НЕВИДИМКОЙ...</div>';
        return;
    }
    
    vacs.forEach(vacancy => {
        const card = document.createElement('div');
        card.className = 'vacancy-card';
        card.innerHTML = `
            <div class="vacancy-title">${vacancy.title}</div>
            <div class="vacancy-salary">${vacancy.salary || 'ЗАРПЛАТА НЕ УКАЗАНА (ВОЗМОЖНО, ОПЛАТА ВОЛШЕБНЫМИ БОБАМИ)'}</div>
            <div class="vacancy-company">${vacancy.company}</div>
            <div>${vacancy.description}</div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                ОПЫТ: ${getExperienceText(vacancy.experience)} | 
                ТИП: ${getEmploymentText(vacancy.employment)}
            </div>
        `;
        resultsContainer.appendChild(card);
    });
}

// Обновление select с вакансиями
function updateVacancySelect() {
    const select = document.getElementById('selectedVacancy');
    select.innerHTML = '<option value="">-- ВЫБЕРИТЕ ВАКАНСИЮ --</option>';
    
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
        showMessage('errorMessage', 'НИЧЕГО НЕ НАЙДЕНО! ВОЗМОЖНО, НУЖНО ИСПОЛЬЗОВАТЬ "REVELIO"');
    } else {
        showMessage('successMessage', `НАЙДЕНО ${filteredVacancies.length} ВАКАНСИЙ! ФИЛЬТРАЦИО СРАБОТАЛО!`);
    }
}

// Генерация письма
function generateLetter() {
    const vacancyId = document.getElementById('selectedVacancy').value;
    const template = document.getElementById('letterTemplate').value;
    const customText = document.getElementById('customText').value;
    
    if (!vacancyId) {
        showMessage('errorMessage', 'ВЫБЕРИТЕ ВАКАНСИЮ! ДАЖЕ ГЕРМИОНА НЕ МОЖЕТ ПИСАТЬ ПИСЬМА НИ О ЧЕМ.');
        return;
    }
    
    const vacancy = vacancies.find(v => v.id == vacancyId);
    let letter = '';
    
    switch(template) {
        case 'support':
            letter = `УВАЖАЕМЫЕ КОЛЛЕГИ ИЗ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ПИШУ ПО ПОВОДУ ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ РАБОТЫ С ${vacancy.description.split(' ').slice(0, 3).join(' ').toUpperCase()}...\n\n` +
                     `КАК ГЕРМИОНА ГРЕЙНДЖЕР, Я ВНИМАТЕЛЬНА К ДЕТАЛЯМ И ВСЕГДА ВЫПОЛНЯЮ РАБОТУ ВОВРЕМЯ.\n\n` +
                     `С УВАЖЕНИЕМ,\nВАШ СОИСКАТЕЛЬ`;
            break;
            
        case 'devops':
            letter = `УВАЖАЕМЫЕ ПРЕДСТАВИТЕЛИ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ЗАИНТЕРЕСОВАН В ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ РАБОТЫ В DEVOPS СОСТАВЛЯЕТ 4 ГОДА (ЭТО КАК 4 ГОДА В ХОГВАРТСЕ, НО БЕЗ КАНИКУЛ).\n\n` +
                     `КАК РОН УИЗЛИ, Я МОГУ НАЙТИ РЕШЕНИЕ ДАЖЕ В САМЫХ СЛОЖНЫХ СИТУАЦИЯХ.\n\n` +
                     `С УВАЖЕНИЕМ`;
            break;
            
        default:
            letter = `УВАЖАЕМЫЕ ПРЕДСТАВИТЕЛИ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ПИШУ ПО ПОВОДУ ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ И НАВЫКИ СООТВЕТСТВУЮТ ВАШИМ ТРЕБОВАНИЯМ (ИЛИ Я БЫСТРО НАУЧУСЬ, КАК ГАРРИ ПОТТЕР УЧИЛСЯ ПАТРОНУСУ).\n\n` +
                     `С УВАЖЕНИЕМ`;
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
    
    showMessage('successMessage', 'ПИСЬМО СОЗДАНО! ГОТОВО К ОТПРАВКЕ СОВИНОЙ ПОЧТОЙ!');
}

// Сохранение письма
function saveLetter() {
    showMessage('successMessage', 'ПИСЬМО СОХРАНЕНО В КУБОК ОГНЯ!');
    
    const btn = event.target;
    btn.textContent = 'СОХРАНЕНО! (ОЖИДАЕТ СОВЫ)';
    btn.style.backgroundColor = '#1a472a';
    setTimeout(() => {
        btn.textContent = 'СОХРАНИТЬ В КУБОК ОГНЯ';
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
            data += `КОМПАНИЯ: ${vac.company}\n`;
            data += `ЗАРПЛАТА: ${vac.salary || 'НЕ УКАЗАНА'}\n`;
            data += `ОПИСАНИЕ: ${vac.description}\n\n`;
        });
    }
    
    if (exportContent === 'letters' || exportContent === 'all') {
        data += '\nПИСЬМА:\n\n';
        generatedLetters.forEach((letter, idx) => {
            const vac = vacancies.find(v => v.id == letter.vacancyId);
            data += `ПИСЬМО #${idx + 1} (${vac.title})\n`;
            data += `${letter.text}\n\n`;
        });
    }
    
    alert(`ЭКСПОРТ В ${exportType.toUpperCase()}!\n\n${data}`);
    showMessage('successMessage', `ЭКСПОРТИРОВАНО В ${getExportTypeText(exportType)}!`);
}

// Вспомогательные функции
function getExperienceText(code) {
    const experiences = {
        'no': 'БЕЗ ОПЫТА (КАК У ПЕРВОКУРСНИКОВ)',
        '1-3': '1-3 ГОДА (КАК У СТАРШЕКУРСНИКОВ)',
        '3-6': '3-6 ЛЕТ (КАК У ВЫПУСКНИКОВ ХОГВАРТСА)',
        '6+': 'БОЛЕЕ 6 ЛЕТ (КАК У ПРОФЕССОРОВ)'
    };
    return experiences[code] || 'НЕИЗВЕСТНО';
}

function getEmploymentText(code) {
    const employments = {
        'full': 'ПОЛНАЯ (КАК У ДИРЕКТОРА ШКОЛЫ)',
        'part': 'ЧАСТИЧНАЯ (КАК У ПРЕПОДАВАТЕЛЯ ПО СОВМЕСТИТЕЛЬСТВУ)',
        'remote': 'УДАЛЕННАЯ (КАК У СОВЕТНИКОВ МИНИСТЕРСТВА)',
        'project': 'ПРОЕКТНАЯ (КАК У ОХОТНИКОВ ЗА ТЕМНЫМИ АРТЕФАКТАМИ)'
    };
    return employments[code] || 'НЕИЗВЕСТНО';
}

function getExportTypeText(type) {
    const types = {
        'docx': 'ПЕРГАМЕНТ (DOCX)',
        'pdf': 'МАГИЧЕСКИЙ СВИТОК (PDF)',
        'txt': 'СВИТОК СОВЫ (TXT)',
        'csv': 'ТАБЛИЦА ПРЕДСКАЗАНИЙ (CSV)',
        'xlsx': 'КНИГА ЗАКЛИНАНИЙ (XLSX)'
    };
    return types[type] || type.toUpperCase();
}