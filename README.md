# CV Builder Web Application

A Django-based web application for creating professional CVs with multiple templates.

## Features
- User authentication (register, login, logout)
- Create and manage multiple CVs
- Three professional templates (Classic, Modern, Minimal)
- PDF export via browser print
- Responsive design

## Installation

1. Create virtual environment
   
   Windows:
   ```powershell
   python -m venv venv
   .\venv\Scripts\python -m pip install --upgrade pip
   .\venv\Scripts\pip install -r requirements.txt
   ```

2. Migrations
   ```powershell
   .\venv\Scripts\python manage.py makemigrations
   .\venv\Scripts\python manage.py migrate
   ```

3. Create superuser (optional)
   ```powershell
   .\venv\Scripts\python manage.py createsuperuser
   ```

4. Populate templates
   ```powershell
   .\venv\Scripts\python manage.py populate_templates
   ```
5. Run server
   ```powershell
   .\venv\Scripts\python manage.py runserver
   `
## 6. Screenshots

Example files:
- static/img/screenshots/homepage.png
- static/img/screenshots/dashboard.png
- static/img/screenshots/editor.png
- static/img/template_preview/preview_classic.png
- static/img/tempalte_preview/preview_modern.png
- static/img/template_preview/preview_minimal.png

Visit http://127.0.0.1:8000/
