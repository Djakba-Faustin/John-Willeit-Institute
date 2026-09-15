# John Willeit Institute - Learning Management System (LMS)

![Logo](logo1.png)

A comprehensive, professional Learning Management System platform built for the John Willeit Institute. This Django-based application provides a complete suite of tools for academic management, student engagement, and institutional operations.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## 🎯 Overview

The **John Willeit Institute LMS** is a complete digital learning platform designed to streamline academic operations and enhance student engagement. Built on Django with a modern web interface, it provides institutions with powerful tools for course management, student tracking, and administrative oversight.

**Version:** 1.0.0  
**Status:** Active Development  
**Organization:** John Willeit Institute

---

## ✨ Key Features

### 📚 Academic Management
- **Course Management**: Create, manage, and organize courses and curricula
- **Class Scheduling**: Automated scheduling and timetable management
- **Curriculum Planning**: Structured course hierarchies and learning paths
- **Assessment Tools**: Quizzes, assignments, and grading systems
- **Academic Calendar**: Term/semester management and event tracking

### 👥 Student Management
- **Student Enrollment**: Streamlined registration and enrollment workflows
- **Academic Profiles**: Comprehensive student records and progress tracking
- **Performance Monitoring**: Real-time grade tracking and analytics
- **Attendance Tracking**: Attendance management and reporting
- **Student Communication**: Announcements, notifications, and messaging

### 👨‍🏫 Instructor Tools
- **Course Content Delivery**: Upload and manage learning materials
- **Assignment Distribution**: Create and distribute assignments with deadlines
- **Grade Management**: Flexible grading systems and rubrics
- **Class Analytics**: Student performance insights and dashboards
- **Communication Center**: Direct messaging with students

### 🔐 Account Management
- **Multi-Role Support**: Admin, Instructor, Student, and Staff roles
- **Authentication**: Secure login and account management
- **User Profiles**: Customizable user information and preferences
- **Permission Management**: Fine-grained access control
- **Audit Logging**: Activity tracking and compliance logging

### 📊 Dashboard & Analytics
- **Admin Dashboard**: Institutional overview and KPIs
- **Student Dashboard**: Personal progress and upcoming tasks
- **Instructor Dashboard**: Class management and grading
- **Analytics & Reports**: Customizable reports and data visualization
- **Real-time Notifications**: Important alerts and updates

### 🌐 Additional Features
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **File Management**: Document storage and sharing
- **Email Integration**: Automated email notifications
- **SSL/TLS Security**: Enterprise-grade encryption
- **PostgreSQL Database**: Reliable and scalable data management

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | Django | ≥4.2, <5.0 |
| **Database** | PostgreSQL | Latest |
| **Server** | Gunicorn | Latest |
| **ASGI Server** | Uvicorn | Latest |
| **Frontend** | HTML5, CSS3 | Modern |
| **Image Processing** | Pillow | Latest |
| **Static Files** | WhiteNoise | Latest |
| **Environment** | Python | 3.8+ |

### Key Dependencies
```
Django>=4.2,<5.0          # Web framework
dj-database-url           # Database URL parsing
gunicorn                  # WSGI HTTP Server
uvicorn                   # ASGI server
Pillow                    # Image processing
psycopg2-binary           # PostgreSQL adapter
python-dotenv             # Environment variable management
whitenoise[brotli]        # Static file serving
```

---

## 🏗️ System Architecture

```
John Willeit Institute LMS
├── Core Services
│   ├── Authentication & Authorization
│   ├── User Management
│   └── Audit Logging
├── Academic Module (academics/)
│   ├── Courses & Curriculum
│   ├── Scheduling
│   └── Assessments
├── LMS Core (jw_lms/)
│   ├── Settings & Configuration
│   ├── URL Routing
│   └── Middleware
├── Account Management (accounts/)
│   ├── User Accounts
│   ├── Profiles
│   └── Permissions
├── Frontend (templates/, static/)
│   ├── HTML Templates
│   ├── CSS Styling
│   └── Static Assets
└── Database Layer
    └── PostgreSQL
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **PostgreSQL**: 12 or higher
- **Git**: For version control
- **Virtual Environment**: `venv` or `virtualenv`

### System Requirements

- **OS**: Linux, macOS, or Windows
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: Minimum 2GB free space
- **Internet**: Required for external services

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Djakba-Faustin/John-Willeit-Institute.git
cd John-Willeit-Institute
```

### Step 2: Create Virtual Environment

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Database Setup

Ensure PostgreSQL is running and create a database:

```bash
createdb jwhi_lms
```

### Step 5: Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

### Step 6: Run Migrations

```bash
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## ⚙️ Configuration

### Environment Variables

Edit your `.env` file with the following configuration:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to True for development only
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/jwhi_lms
DB_SSL_REQUIRE=False

# Email Configuration (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@johnwilleit.edu
```

### Database Configuration

PostgreSQL database setup:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE jwhi_lms;
CREATE USER jwhi_user WITH PASSWORD 'secure_password';
ALTER ROLE jwhi_user SET client_encoding TO 'utf8';
ALTER ROLE jwhi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jwhi_user SET default_transaction_deferrable TO on;
ALTER ROLE jwhi_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jwhi_lms TO jwhi_user;
```

---

## 🏃 Running the Application

### Development Server

```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000`

Admin panel: `http://127.0.0.1:8000/admin`

### Production Server (Using Gunicorn)

```bash
gunicorn jw_lms.wsgi:application --bind 0.0.0.0:8000
```

### Using ASGI (Uvicorn)

```bash
uvicorn jw_lms.asgi:application --host 0.0.0.0 --port 8000
```

### Build & Deploy Script

```bash
bash build.sh
```

---

## 📁 Project Structure

```
John-Willeit-Institute/
├── academics/              # Academic management module
│   ├── models.py          # Course, class, assessment models
│   ├── views.py           # Academic views
│   └── urls.py            # Academic URL routing
├── accounts/              # User account management
│   ├── models.py          # User, profile models
│   ├── views.py           # Authentication views
│   └── forms.py           # User forms
├── core/                  # Core functionality
│   ├── models.py          # Base models
│   ├── middleware.py      # Custom middleware
│   └── permissions.py     # Permission classes
├── jw_lms/               # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── lms/                  # LMS core module
│   ├── models.py         # LMS-specific models
│   ├── views.py          # LMS views
│   └── urls.py           # LMS URL routing
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard/        # Dashboard templates
│   ├── courses/          # Course templates
│   └── accounts/         # Account templates
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
├── render.yaml           # Render deployment config
└── README.md             # This file
```

---

## 📚 API Documentation

### Authentication Endpoints

```
POST   /api/auth/login/              - User login
POST   /api/auth/logout/             - User logout
POST   /api/auth/register/           - New user registration
POST   /api/auth/refresh-token/      - Refresh authentication token
GET    /api/auth/profile/            - Get user profile
PUT    /api/auth/profile/            - Update user profile
```

### Academic Endpoints

```
GET    /api/courses/                 - List all courses
POST   /api/courses/                 - Create new course
GET    /api/courses/<id>/            - Get course details
PUT    /api/courses/<id>/            - Update course
DELETE /api/courses/<id>/            - Delete course

GET    /api/classes/                 - List all classes
GET    /api/assignments/             - List assignments
POST   /api/assignments/             - Create assignment
GET    /api/grades/                  - Get grades
POST   /api/grades/                  - Submit grade
```

### Student Endpoints

```
GET    /api/students/                - List students
GET    /api/students/<id>/           - Get student details
GET    /api/students/<id>/progress/  - Get student progress
GET    /api/students/<id>/grades/    - Get student grades
```

For detailed API documentation, see: [API_DOCS.md](docs/API_DOCS.md)

---

## 🗄️ Database

### Schema Overview

**Users Table**
- User authentication and basic information
- Roles: Admin, Instructor, Student, Staff

**Courses Table**
- Course information and metadata
- Course codes, descriptions, credits

**Classes Table**
- Class sections and schedules
- Instructor assignments, room allocation

**Enrollments Table**
- Student course enrollments
- Enrollment status and dates

**Assignments Table**
- Assignment details and deadlines
- Submission requirements

**Grades Table**
- Student grades and scores
- Assessment results

**Attendance Table**
- Attendance records
- Session tracking

---

## 🌐 Deployment

### Render.com Deployment

The application includes `render.yaml` for easy deployment on Render:

```yaml
services:
  - type: web
    name: jwhi-lms
    env: python
    plan: standard
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate"
    startCommand: "gunicorn jw_lms.wsgi:application"
    envVars:
      - key: DJANGO_SECRET_KEY
        value: # Set in dashboard
      - key: DATABASE_URL
        fromDatabase:
          name: postgres-db
          property: connectionString
```

### Deploy Steps

1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy

Access: `https://your-app.onrender.com`

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "jw_lms.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write tests for new features
- Update documentation
- Ensure all tests pass: `python manage.py test`

### Code Standards

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .

# Run tests
python manage.py test --verbosity=2
```

---

## 💬 Support

### Getting Help

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Open an issue on GitHub
- **Email**: support@johnwilleit.edu
- **FAQ**: See [FAQ.md](docs/FAQ.md)

### Reporting Bugs

Please provide:
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment information

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Djakba-Faustin**
- GitHub: [@Djakba-Faustin](https://github.com/Djakba-Faustin)
- Email: faustindjakba780@gmail.com

---

## 🙏 Acknowledgments

- Django community for excellent documentation
- PostgreSQL for reliable database
- Render for hosting solutions
- John Willeit Institute for inspiration

---

## 📈 Roadmap

### Version 1.1 (Q4 2026)
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] AI-powered student recommendations
- [ ] Video conferencing integration

### Version 1.2 (Q1 2027)
- [ ] Blockchain certificates
- [ ] Third-party LTI integration
- [ ] Advanced reporting tools
- [ ] Multi-language support

---

## 🔗 Useful Links

- [Official Website](#) - John Willeit Institute
- [Documentation](docs/README.md) - Full documentation
- [Issue Tracker](#) - Report bugs
- [Discussion Forum](#) - Community discussions

---

**Last Updated**: September 15, 2026  
**Status**: Active Development  
**Current Version**: 1.0.0

For questions or more information, please visit our repository or contact the development team.
