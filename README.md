# Student Tutoring System

A Django-based web application for connecting students with tutors.

## Features

- User Registration and Authentication
- Profile Management
- Tutor Search Functionality
- Scheduling System
- Messaging System
- Online Tutoring
- Review and Rating System

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tutoring_system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://127.0.0.1:8000/ in your browser

## Project Structure

- `core/` - Main application directory
  - `models.py` - Database models
  - `views.py` - View functions
  - `urls.py` - URL routing
  - `forms.py` - Form definitions
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `fixtures/` - Sample data

## Usage

1. Register as a student or tutor
2. Complete your profile
3. Search for tutors (if you're a student)
4. Book sessions
5. Communicate through the messaging system
6. Rate and review tutors after sessions 