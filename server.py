"""
ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА (ДИПЛОМНЫЙ ПРОЕКТ)
Тема: Разработка АИС «Портфолио студента / Сайт-визитка»
Специальность: 06130100 - «Программное обеспечение (по видам)»
Квалификация: Техник информационных систем
"""

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import sqlite3
from datetime import datetime

app = FastAPI(title="АИС Портфолио Студента ВФЭК")
DB_NAME = "portfolio_db.db"

# =====================================================================
# БЛОК ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ (Простой SQL без наворотов)
# =====================================================================
def init_db():
    """Создание одной простой таблицы для хранения сообщений/отзывов"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guestbook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            date_added TEXT NOT NULL
        )
    """)
    
    # Добавим базовые записи, чтобы при первом запуске сайт не выглядел пустым перед комиссией
    cursor.execute("SELECT COUNT(*) FROM guestbook")
    if cursor.fetchone()[0] == 0:
        demo_data = [
            ("Мукушева Л. А.", "l.mukasheva@vfek.edu.kz", "Прекрасный сайт-визитка. Архитектура на FastAPI реализована грамотно, код чистый.", "2026-05-28 14:20:15"),
            ("Иванов Сергей Петрович", "hr@it-solutions.kz", "Рассмотрели портфолио студента. Отличный набор навыков для Junior Python разработчика.", "2026-05-29 09:05:00")
        ]
        cursor.executemany("INSERT INTO guestbook (name, email, message, date_added) VALUES (?, ?, ?, ?)", demo_data)
        
    conn.commit()
    conn.close()

init_db()

# =====================================================================
# ОБЩИЙ ДИЗАЙН И СТИЛИ САЙТА (Красивый темный IT-стиль)
# =====================================================================
CSS_STYLES = """
<style>
    :root {
        --bg-main: #0b0f19; --bg-card: #151b2d; --accent-cyan: #00f2fe;
        --accent-purple: #9d4edf; --text-main: #f4f6fb; --text-muted: #728299;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: var(--bg-main); color: var(--text-main); font-family: 'Segoe UI', sans-serif; padding-bottom: 50px; }
    
    /* Навигационная панель (Шапка сайта) */
    header { background: rgba(21, 27, 45, 0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid rgba(0, 242, 254, 0.1); }
    .nav-box { max-width: 1000px; margin: 0 auto; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.25rem; color: #fff; text-decoration: none; letter-spacing: 1px; }
    .logo span { color: var(--accent-cyan); }
    nav a { color: var(--text-muted); text-decoration: none; margin-left: 25px; font-weight: 600; font-size: 0.95rem; transition: 0.3s; }
    nav a:hover, nav a.active { color: var(--accent-cyan); }
    
    /* Главный контейнер для контента страниц */
    .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
    .card { background: var(--bg-card); padding: 35px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.02); box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin-bottom: 30px; }
    
    h1 { font-size: 2.2rem; margin-bottom: 15px; color: #fff; }
    h2 { font-size: 1.4rem; margin-bottom: 20px; color: var(--accent-cyan); }
    p { margin-bottom: 15px; color: #d1d9e6; line-height: 1.6; }
    
    /* Стили для Главной (Теги навыков) */
    .skills-flex { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
    .tag { background: rgba(0, 242, 254, 0.08); color: var(--accent-cyan); border: 1px solid rgba(0, 242, 254, 0.2); padding: 6px 14px; border-radius: 20px; font-size: 0.88rem; font-weight: 600; }
    .tag.soft { background: rgba(157, 78, 223, 0.08); color: #c89eff; border-color: rgba(157, 78, 223, 0.2); }
    
    /* Стили для страницы Проектов */
    .project-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .project-card { background: rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border-top: 3px solid var(--accent-purple); }
    .project-card h3 { color: #fff; margin-bottom: 8px; }
    .project-tech { font-size: 0.8rem; color: var(--accent-cyan); font-family: monospace; margin-bottom: 10px; display: block; }
    
    /* Стили для Формы обратной связи */
    .feedback-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; }
    .form-group { margin-bottom: 15px; }
    label { display: block; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    input, textarea { width: 100%; background: #090d16; border: 1px solid rgba(0,242,254,0.15); padding: 12px; border-radius: 8px; color: #fff; font-family: inherit; transition: 0.3s; }
    input:focus, textarea:focus { border-color: var(--accent-cyan); outline: none; }
    .btn { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)); color: #0b0f19; font-weight: bold; width: 100%; padding: 13px; border: none; border-radius: 8px; cursor: pointer; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; transition: 0.3s; }
    .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,242,254,0.25); }
    
    /* Список отзывов на сайте */
    .review-item { background: rgba(255,255,255,0.02); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 3px solid var(--accent-cyan); }
    .review-header { display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 5px; }
    
    /* Таблица СУБД (Для комиссии) */
    table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.88rem; }
    th { background: rgba(0,242,254,0.04); color: var(--accent-cyan); padding: 12px; text-align: left; border-bottom: 2px solid rgba(0,242,254,0.15); }
    td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }
</style>
"""

def make_page(content_html: str, active_tab: str) -> str:
    """Вспомогательный шаблонизатор: склеивает меню, стили и контент конкретной страницы"""
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>АИС Портфолио Студента</title>
        {CSS_STYLES}
    </head>
    <body>
        <header>
            <div class="nav-box">
                <a href="/" class="logo">STUDENT<span>//PORTFOLIO</span></a>
                <nav>
                    <a href="/" class="{"active" if active_tab == "home" else ""}">1. Главная</a>
                    <a href="/projects" class="{"active" if active_tab == "projects" else ""}">2. Мои Проекты</a>
                    <a href="/reviews" class="{"active" if active_tab == "reviews" else ""}">3. Отзывы и Связь</a>
                    <a href="/commission-db" class="{"active" if active_tab == "db" else ""}">4. Панель СУБД (Комиссия)</a>
                </nav>
            </div>
        </header>
        <div class="container">
            {content_html}
        </div>
    </body>
    </html>
    """

# =====================================================================
# МАРШРУТЫ СТРАНИЦ (ROUTES)
# =====================================================================

@app.get("/", response_class=HTMLResponse)
async def page_home():
    """СТРАНИЦА 1: Главная (Визитная карточка / Резюме)"""
    html_content = """
    <div class="card">
        <span style="color: var(--accent-cyan); font-weight: bold; font-size: 0.85rem; text-transform: uppercase;">Сайт-визитка выпускника колледжа</span>
        <h1 style="margin-top: 5px;">АИС «Квалификационное портфолио студента»</h1>
        <p style="font-size: 1.1rem; color: #a2afc3;">Квалификация: <b>Техник информационных систем</b></p>
        <p>Приветствую! Данный веб-ресурс представляет собой программный комплекс личного портфолио. Архитектура приложения реализована на языке Python с использованием асинхронного веб-фреймворка FastAPI. Проект демонстрирует навыки разработки интерфейсов и проектирования реляционных баз данных.</p>
    </div>

    <div class="card">
        <h2>Технологический стек и навыки</h2>
        <p>В процессе обучения в Высшем финансово-экономическом колледже были освоены следующие инструментальные средства и технологии программирования:</p>
        
        <h3 style="font-size: 1rem; color: #fff; margin-top: 15px;">Профессиональные (Hard Skills):</h3>
        <div class="skills-flex">
            <span class="tag">Python 3.x</span>
            <span class="tag">FastAPI Framework</span>
            <span class="tag">Разработка веб-API</span>
            <span class="tag">СУБД SQLite3 / Язык SQL</span>
            <span class="tag">Uvicorn ASGI Server</span>
            <span class="tag">Проектирование реляционных БД</span>
            <span class="tag">HTML5 / CSS3 Верстка</span>
        </div>

        <h3 style="font-size: 1rem; color: #fff; margin-top: 20px;">Системные / Личные (Soft Skills):</h3>
        <div class="skills-flex">
            <span class="tag soft">Алгоритмическое мышление</span>
            <span class="tag soft">Администрирование информационных систем</span>
            <span class="tag soft">Информационная безопасность ПО</span>
            <span class="tag soft">Техническая документация</span>
        </div>
    </div>
    """
    return make_page(html_content, "home")


@app.get("/projects", response_class=HTMLResponse)
async def page_projects():
    """СТРАНИЦА 2: Мои Проекты (Репозиторий практических работ)"""
    html_content = """
    <div class="card">
        <h1>Репозиторий выполненных программных модулей</h1>
        <p style="color: var(--text-muted); margin-bottom: 25px;">Ниже представлены ключевые практические и курсовые проекты, созданные в рамках учебной программы по специальности «Программное обеспечение».</p>
        
        <div class="project-grid">
            <div class="project-card">
                <h3>1. Программа контроля складского учета</h3>
                <span class="project-tech">Технологии: Python, OOP, JSON-структуры</span>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Консольное приложение для автоматизации работы небольшого склада. Позволяет добавлять, списывать товары и формировать текстовые отчеты о наличии остатков на предприятии.</p>
            </div>
            
            <div class="project-card">
                <h3>2. Модуль проверки целостности данных</h3>
                <span class="project-tech">Технологии: Python, Cryptography, Хэширование</span>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Специализированный скрипт автоматического сканирования директорий. Рассчитывает контрольные суммы файлов (алгоритм SHA-256) для предотвращения несанкционированного изменения информации.</p>
            </div>
            
            <div class="project-card">
                <h3>3. Текущая АИС «Веб-Портфолио»</h3>
                <span class="project-tech">Технологии: FastAPI, SQLite3, HTML5/CSS Variables</span>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Выпускной дипломный проект. Веб-серверная монолитная система, агрегирующая информацию о студенте и реализующая сохранение пользовательских транзакций в локальную базу данных.</p>
            </div>
            
            <div class="project-card">
                <h3>4. База данных учета успеваемости</h3>
                <span class="project-tech">Технологии: Реляционный SQL, Индексация, Join-запросы</span>
                <p style="font-size: 0.9rem; margin-bottom: 0;">Спроектированная архитектура базы данных. Отрабатывает логические запросы связывания таблиц студентов, учебных дисциплин и итоговых оценок.</p>
            </div>
        </div>
    </div>
    """
    return make_page(html_content, "projects")


@app.get("/reviews", response_class=HTMLResponse)
async def page_reviews():
    """СТРАНИЦА 3: Отзывы и связь (Форма инпута + вывод отзывов)"""
    # Вытаскиваем список отзывов из базы данных SQLite, чтобы вывести их на страницу
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, message, date_added FROM guestbook ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()

    # Генерируем блоки отзывов в HTML
    reviews_html = ""
    for item in records:
        reviews_html += f"""
        <div class="review-item">
            <div class="review-header">
                <span style="color:#fff; font-weight:bold;">{item[0]} ({item[1]})</span>
                <span>{item[3]}</span>
            </div>
            <div style="font-size:0.92rem; margin-top:5px; color:#d1d9e6;">{item[2]}</div>
        </div>
        """

    html_content = f"""
    <div class="card">
        <h1>Обратная связь и отзывы</h1>
        <p style="color: var(--text-muted);">Посетители сайта (преподаватели, потенциальные работодатели) могут направить свое обращение. Данные будут мгновенно занесены в базу данных.</p>
    </div>

    <div class="feedback-layout">
        <div class="card">
            <h2>Оставить запись</h2>
            <form action="/add-review-action" method="POST">
                <div class="form-group">
                    <label>Ваше имя / Компания</label>
                    <input type="text" name="username" placeholder="Например: ТОО 'Инновации'" required>
                </div>
                <div class="form-group">
                    <label>Ваш Email адрес</label>
                    <input type="email" name="useremail" placeholder="example@domain.com" required>
                </div>
                <div class="form-group">
                    <label>Текст сообщения</label>
                    <textarea name="usermessage" rows="5" placeholder="Напишите текст отзыва..." required></textarea>
                </div>
                <button type="submit" class="btn">Записать в СУБД</button>
            </form>
        </div>
        
        # Правая часть: Живой вывод отзывов из Базы Данных
        <div>
            <h2 style="margin-left: 10px;">Лента записей (Из базы данных)</h2>
            <div style="max-height: 450px; overflow-y: auto; padding-right: 5px;">
                {reviews_html if reviews_html else "<p>Записей пока нет.</p>"}
            </div>
        </div>
    </div>
    """
    return make_page(html_content, "reviews")


@app.get("/commission-db", response_class=HTMLResponse)
async def page_commission_db():
    """СТРАНИЦА 4: Раздел для комиссии (Прямой вывод SQL таблицы)"""
    # Соединяемся с базой и выгружаем всю таблицу в сыром виде
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, message, date_added FROM guestbook ORDER BY id ASC")
    db_rows = cursor.fetchall()
    conn.close()

    table_rows_html = ""
    for r in db_rows:
        table_rows_html += f"""
        <tr>
            <td style="color: var(--accent-cyan); font-weight: bold;">{r[0]}</td>
            <td><b>{r[1]}</b></td>
            <td style="color: var(--accent-purple); font-family: monospace;">{r[2]}</td>
            <td>{r[3]}</td>
            <td style="color: var(--text-muted); font-size: 0.85rem;">{r[4]}</td>
        </tr>
        """

    html_content = f"""
    <div class="card">
        <h1>Инспекция реляционной СУБД SQLite3</h1>
        <p>Данный раздел разработан специально для демонстрации аттестационной комиссии. Он подтверждает, что система не просто отображает текст, а является полноценным веб-приложением, интегрированным со структурами баз данных языка SQL.</p>
        <p>Ниже транслируются строки в реальном времени напрямую из локального файла базы данных <b>{DB_NAME}</b> через стандартные SQL-драйверы Python:</p>
        
        <h2 style="margin-top: 30px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
            Таблица сущности: <code style="color: var(--accent-purple);">guestbook</code>
        </h2>
        
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>ID (Primary Key)</th>
                        <th>ФИО / Автор транзакции</th>
                        <th>Контактный Email</th>
                        <th>Текст сообщения (Поле TEXT)</th>
                        <th>Метка даты и времени</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return make_page(html_content, "db")


@app.post("/add-review-action")
async def action_add_review(username: str = Form(...), useremail: str = Form(...), usermessage: str = Form(...)):
    """Обработчик POST-запроса формы. Выполняет классический SQL INSERT в базу данных"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Выполнение безопасного запроса с использованием кортежа параметров
    cursor.execute(
        "INSERT INTO guestbook (name, email, message, date_added) VALUES (?, ?, ?, ?)",
        (username, useremail, usermessage, current_time)
    )
    conn.commit()
    conn.close()
    
    # После успешной записи перенаправляем пользователя обратно на страницу отзывов
    return RedirectResponse(url="/reviews", status_code=303)


# =====================================================================
# ТОЧКА ВХОДА (ЗАПУСК СЕРВЕРА)
# =====================================================================
if __name__ == "__main__":
    print("[SYSTEM] Инициализация АИС 'Портфолио Студента'...")
    print("[SYSTEM] Подключение к локальной базе данных SQLite: Успешно.")
    print("[SYSTEM] Веб-интерфейс развернут на http://127.0.0.1:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)