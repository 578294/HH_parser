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

// Переключение вкладок (без эффекта тряски)
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
        showMessage('errorMessage', 'ЭЙ, ДАЙ ССЫЛКУ! КАК КАРТМАН ГОВОРИТ: "У МЕНЯ НЕТ ВРЕМЕНИ НА ЭТУ ДИЧЬ!"');
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
                    'ПАРСИМ ВАКАНСИИ' + '.'.repeat(dots % 4);
                dots++;
            }, 300);
            
            setTimeout(() => {
                clearInterval(interval);
                resolve();
            }, 2000);
        });
        
        // Тестовые данные с юмором South Park
        vacancies = [
            {
                id: 1,
                title: "PYTHON РАЗРАБОТЧИК",
                salary: "150 000 РУБ. (НЕ КАК У МИСТЕРА ГАРРИСОНА)",
                company: "ООО 'ТЕХНОЛАБ' (НЕ ПУТАТЬ С ТЕХНОЛОЖЬЮ)",
                description: "ИЩЕМ ОПЫТНОГО PYTHON РАЗРАБОТЧИКА ДЛЯ ВЫСОКОНАГРУЖЕННОГО ПРОЕКТА. ОПЫТ РАБОТЫ С КАРТМАНОМ БУДЕТ ПЛЮСОМ.",
                experience: "1-3",
                employment: "full"
            },
            {
                id: 2,
                title: "DEVOPS ИНЖЕНЕР",
                salary: "$3000 - $5000 (КАК У TOKEN, НО БЕЗ ПАПЫ)",
                company: "INTERNATIONAL TECH CORP (НЕ ПУТАТЬ С SHEF'S SALTY SPOON)",
                description: "REMOTE POSITION FOR DEVOPS EXPERT WITH 3+ YEARS EXPERIENCE. NO CANADIANS (SORRY, KYLE).",
                experience: "3-6",
                employment: "remote"
            },
            {
                id: 3,
                title: "МЕНЕДЖЕР ПРОЕКТОВ",
                salary: "200 000 РУБ. (ПЛЮС БОНУСЫ КАК У MR. SLAVE)",
                company: "ООО 'CHEESY POOFS'",
                description: "НУЖЕН МЕНЕДЖЕР, КОТОРЫЙ СПРАВИТСЯ С ТАКИМИ КЛИЕНТАМИ, КАК КАРТМАН. ОПЫТ РАБОТЫ С ДЕТЬМИ ПРИВЕТСТВУЕТСЯ.",
                experience: "6+",
                employment: "full"
            }
        ];
        
        displayVacancies(vacancies);
        updateVacancySelect();
        showMessage('successMessage', `НАПАРСИЛИ ${vacancies.length} ВАКАНСИЙ! ТЕПЕРЬ МОЖНО ИДТИ К МАКДОНАЛДС!`);
        
    } catch (error) {
        showMessage('errorMessage', `ОШИБКА: ${error.message.toUpperCase()}! КАК ГОВОРИТ КАРТМАН: "ВЫ ВСЕ ОТСТОЙ!"`);
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
        resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center;">НИЧЕГО НЕ НАЙДЕНО! СОВСЕМ КАК У КЕНИ, КОГДА ОН ИЩЕТ СВОЙ МОЗГ...</div>';
        return;
    }
    
    vacs.forEach(vacancy => {
        const card = document.createElement('div');
        card.className = 'vacancy-card';
        card.innerHTML = `
            <div class="vacancy-title">${vacancy.title}</div>
            <div class="vacancy-salary">${vacancy.salary || 'ЗАРПЛАТА НЕ УКАЗАНА (НАВЕРНОЕ, КАК У МИСТЕРА МЕККИ)'}</div>
            <div class="vacancy-company">${vacancy.company}</div>
            <div>${vacancy.description}</div>
            <div style="margin-top: 10px; font-size: 0.9em;">
                Опыт: ${getExperienceText(vacancy.experience)} | 
                Тип: ${getEmploymentText(vacancy.employment)}
            </div>
        `;
        resultsContainer.appendChild(card);
    });
}

// Обновление select с вакансиями
function updateVacancySelect() {
    const select = document.getElementById('selectedVacancy');
    select.innerHTML = '<option value="">-- ВЫБЕРИ ВАКАНСИЮ --</option>';
    
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
        // Фильтр по ключевым словам
        if (keywords && 
            !vac.title.toLowerCase().includes(keywords) && 
            !vac.description.toLowerCase().includes(keywords) && 
            !vac.company.toLowerCase().includes(keywords)) {
            return false;
        }
        
        // Фильтр по зарплате (упрощенный)
        if (minSalary) {
            const salaryNum = parseInt(vac.salary.replace(/\D/g,''));
            if (isNaN(salaryNum)) return false;
            if (salaryNum < parseInt(minSalary)) return false;
        }
        
        // Фильтр по опыту
        if (experience && vac.experience !== experience) {
            return false;
        }
        
        // Фильтр по типу занятости
        if (employment && vac.employment !== employment) {
            return false;
        }
        
        return true;
    });
    
    displayVacancies(filteredVacancies, 'filterResults');
    
    if (filteredVacancies.length === 0) {
        showMessage('errorMessage', 'НИЧЕГО НЕ НАШЛИ! КАК КАРТМАН, КОГДА ИЩЕТ ДРУЗЕЙ...');
    } else {
        showMessage('successMessage', `НАШЛИ ${filteredVacancies.length} ВАКАНСИЙ! ТЕПЕРЬ МОЖНО ПОЗВАТЬ КЕНИ НА ПОМОЩЬ!`);
    }
}

// Генерация письма
function generateLetter() {
    const vacancyId = document.getElementById('selectedVacancy').value;
    const template = document.getElementById('letterTemplate').value;
    const customText = document.getElementById('customText').value;
    
    if (!vacancyId) {
        showMessage('errorMessage', 'ВЫБЕРИ ВАКАНСИЮ! КАК ГОВОРИТ КАРТМАН: "Я НЕ БУДУ ЭТО ДЕЛАТЬ ЗА ТЕБЯ!"');
        return;
    }
    
    const vacancy = vacancies.find(v => v.id == vacancyId);
    let letter = '';
    
    // Базовый шаблон с юмором South Park
    switch(template) {
        case 'support':
            letter = `УВАЖАЕМЫЕ КОЛЛЕГИ!\n\n` +
                     `Я ХОЧУ РАБОТАТЬ У ВАС НА ДОЛЖНОСТИ "${vacancy.title}"!\n` +
                     `МОЙ ОПЫТ РАБОТЫ С ${vacancy.description.split(' ').slice(0, 3).join(' ').toUpperCase()}...\n\n` +
                     `Я КАК КАРТМАН - СДЕЛАЮ ВСЁ, ЧТОБЫ ВАМ ПОНРАВИТЬСЯ (НО ТОЛЬКО ЕСЛИ ВЫ КУПИТЕ МНЕ CHEESY POOFS).\n\n` +
                     `С УВАЖЕНИЕМ,\nВАШ СОИСКАТЕЛЬ`;
            break;
            
        case 'devops':
            letter = `УВАЖАЕМЫЕ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ИНТЕРЕСУЮСЬ ВАКАНСИЕЙ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ РАБОТЫ В DEVOPS СОСТАВЛЯЕТ 4 ГОДА (ЭТО КАК 28 ЛЕТ ПО ЧЕЛОВЕЧЕСКИ, ЕСЛИ Я КЕНИ).\n\n` +
                     `С УВАЖЕНИЕМ`;
            break;
            
        default:
            letter = `УВАЖАЕМЫЕ ПРЕДСТАВИТЕЛИ ${vacancy.company.toUpperCase()}!\n\n` +
                     `Я ПИШУ ПО ПОВОДУ ВАКАНСИИ "${vacancy.title}".\n` +
                     `МОЙ ОПЫТ И НАВЫКИ СООТВЕТСТВУЮТ ВАШИМ ТРЕБОВАНИЯМ (НУ ИЛИ Я ХОТЯ БЫ ПОПРОБУЮ, КАК БАТТЕРС).\n\n` +
                     `С УВАЖЕНИЕМ`;
    }
    
    // Добавляем кастомный текст
    if (customText) {
        letter += '\n\nP.S. ' + customText.toUpperCase();
    }
    
    const letterContainer = document.getElementById('generatedLetter');
    letterContainer.innerHTML = letter.replace(/\n/g, '<br>');
    document.getElementById('letterResult').style.display = 'block';
    
    // Сохраняем письмо в историю
    generatedLetters.push({
        vacancyId: vacancy.id,
        text: letter,
        date: new Date()
    });
    
    showMessage('successMessage', 'ПИСЬМО СОСТАВЛЕНО! ТЕПЕРЬ МОЖНО ОТПРАВИТЬ ЕГО И ЖДАТЬ ОТВЕТА, КАК КАРТМАН ЖДЁТ CHEESY POOFS!');
}

// Сохранение письма
function saveLetter() {
    showMessage('successMessage', 'СОХРАНЕНО! ТЕПЕРЬ ЭТО ТАК ЖЕ НАДЁЖНО, КАК И ДРУЖБА КАЙЛА И СТЭНА!');
    
    const btn = event.target;
    btn.textContent = 'СОХРАНЕНО! (RESPECT MY AUTHORITAH!)';
    btn.style.backgroundColor = '#8bc53f';
    setTimeout(() => {
        btn.textContent = 'СОХРАНИТЬ ПИСЬМО';
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
            data += `Должность: ${vac.title}\n`;
            data += `Компания: ${vac.company}\n`;
            data += `Зарплата: ${vac.salary || 'Не указана (как у мистера Мекки)'}\n`;
            data += `Описание: ${vac.description}\n\n`;
        });
    }
    
    if (exportContent === 'letters' || exportContent === 'all') {
        data += '\nПИСЬМА:\n\n';
        generatedLetters.forEach((letter, idx) => {
            const vac = vacancies.find(v => v.id == letter.vacancyId);
            data += `Письмо #${idx + 1} (${vac.title})\n`;
            data += `${letter.text}\n\n`;
        });
    }
    
    // В реальном приложении здесь был бы экспорт в файл
    alert(`ЭКСПОРТ В ${exportType.toUpperCase()}!\n\n${data}`);
    
    showMessage('successMessage', `ЭКСПОРТИРОВАНО В ${exportType.toUpperCase()}! ТЕПЕРЬ МОЖНО ПОКАЗАТЬ ЭТО МАМЕ, КАК КАЙЛ!`);
}

// Вспомогательные функции с юмором South Park
function getExperienceText(code) {
    const experiences = {
        'no': 'БЕЗ ОПЫТА (КАК КАРТМАН БЕЗ СОВЕСТИ)',
        '1-3': '1-3 ГОДА (КАК КЕНИ ЧЕРЕЗ 3 ГОДА В 4 КЛАССЕ)',
        '3-6': '3-6 ЛЕТ (КАК СТЭН ПОСЛЕ ШЕСТИ ЛЕТ ПЬЯНСТВА)',
        '6+': 'БОЛЕЕ 6 ЛЕТ (КАК МИСТЕР ГАРРИСОН В ДЕПРЕССИИ)'
    };
    return experiences[code] || 'НЕИЗВЕСТНО (ВОЗМОЖНО, КАК У МИСТЕРА МЕККИ)';
}

function getEmploymentText(code) {
    const employments = {
        'full': 'ПОЛНАЯ (КАК ЖИВОТ У ЧИФА)',
        'part': 'ЧАСТИЧНАЯ (КАК МОЗГИ БАТТЕРСА)',
        'remote': 'УДАЛЕННАЯ (КАК ТВИТТЕР КАЙЛА)',
        'project': 'ПРОЕКТНАЯ (КАК ВСЕ ПРОЕКТЫ ТОКЕНА)'
    };
    return employments[code] || 'НЕИЗВЕСТНО (НАВЕРНОЕ, КАК У КЕНИ)';
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    // South Park эффект загрузки
    setTimeout(() => {
        document.querySelector('h1').style.letterSpacing = '2px';
        setTimeout(() => {
            document.querySelector('h1').style.letterSpacing = '0';
        }, 200);
    }, 500);
});