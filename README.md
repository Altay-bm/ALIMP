# ALIMP Requests — Система управления заявками на оборудование РЗА

Короткое описание
Система для внутреннего использования отдела продаж и техподдержки НПП «АЛИМП»: регистрация клиентских заявок, подбор оборудования, формирование коммерческих предложений и отгрузка.

Стек технологий
- Python 3.11+
- FastAPI
- SQLite
- SQLAlchemy (ORM)
- Jinja2 (шаблоны)
- Uvicorn (ASGI)

Функции
- Три роли: Manager (менеджер), Engineer (инженер), Admin (администратор)
- Создание/редактирование заявок, статусы, назначение инженера
- Комментарии и история действий
- Управление пользователями (админ)
- Простой отчет по статусам и суммам

Тестовые учетки (по умолчанию создаются при первом запуске)
- manager / man123 (Менеджер)
- engineer / eng123 (Инженер)
- admin / admin123 (Администратор)

ER-диаграмма (Mermaid)
```mermaid
classDiagram
  class Users {
    +int id PK
    +string name
    +string username
    +string password_hash
    +string role
  }
  class Requests {
    +int id PK
    +string number
    +datetime created_at
    +string client_name
    +string contact_person
    +string phone
    +string email
    +string equipment_type
    +text technical_params
    +int quantity
    +string status
    +decimal cost
    +int assigned_to_id FK
    +int created_by_id FK
  }
  class Comments {
    +int id PK
    +text text
    +int author_id FK
    +datetime created_at
    +int request_id FK
  }
  class History {
    +int id PK
    +int request_id FK
    +int author_id FK
    +string action
    +datetime created_at
  }

  Users "1" -- "0..*" Requests : creates
  Requests "1" -- "0..*" Comments : has
  Requests "1" -- "0..*" History : logs
  Users "1" -- "0..*" Comments : authors
```


Структура проекта (важные файлы)
- main.py — точка входа приложения
- config.py — настройки, справочники
- database.py — подключение SQLAlchemy
- models.py — ORM модели
- templates/ — Jinja2 шаблоны (base.html, login.html, requests_list.html, request_detail.html,...)
- routers/ — роутеры: auth, requests, users, reports
- static/css/styles.css — стили
- requirements.txt
- .gitignore

Запуск локально (Windows, PowerShell)

1) Перейти в папку проекта:
```
cd "C:\Users\Vlad\Desktop\ALIMP"
```
2) Создать и активировать виртуальное окружение:
```
python -m venv .venv
.\\.venv\\Scripts\\Activate
```
3) Установить зависимости:
```
pip install -r requirements.txt
```
4) Запустить приложение:
```
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Доступ: http://127.0.0.1:8000

Тестовые учётки: manager/man123, engineer/eng123, admin/admin123

Примечания
- Измените SECRET_KEY и пароли перед публикацией.
- Проверьте права доступа пользователей в коде (init_users в main.py).

Use Case (Mermaid)
```mermaid
flowchart LR
  subgraph Actors
    A_Manager(["Менеджер"])
    A_Engineer(["Инженер"])
    A_Admin(["Администратор"])
  end

  subgraph UseCases [Use Cases]
    UC_Login(["Войти в систему"])
    UC_Create(["Создать заявку"])
    UC_Close(["Закрыть заявку"])
    UC_Take(["Взять заявку в работу"])
    UC_Finish(["Перевести в статус \"Выполнено\""])
    UC_Comment(["Добавить комментарий"])
    UC_List(["Просмотреть список заявок"])
    UC_History(["Просмотреть историю заявки"])
    UC_AdminMngr(["Управлять сотрудниками"])
    UC_ResetPwd(["Сменить пароль сотруднику"])
    UC_DeleteUser(["Удалить сотрудника"])
  end

  A_Manager --> UC_Login
  A_Manager --> UC_Create
  A_Manager --> UC_Close
  A_Manager --> UC_List
  A_Manager --> UC_History

  A_Engineer --> UC_Login
  A_Engineer --> UC_Take
  A_Engineer --> UC_Finish
  A_Engineer --> UC_Comment
  A_Engineer --> UC_List
  A_Engineer --> UC_History

  A_Admin --> UC_Login
  A_Admin --> UC_AdminMngr
  A_Admin --> UC_ResetPwd
  A_Admin --> UC_DeleteUser

  %% extends (dashed)
  UC_Create -.-> UC_Login
  UC_Close  -.-> UC_Login
  UC_Take   -.-> UC_Login
```
