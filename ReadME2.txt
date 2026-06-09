I'll provide the content for each file you need to create in your VS Code project. Save these files in the root directory of your `performance_appraisal` project.

## 1. `Dockerfile`

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (required for reportlab and Pillow)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory for background logos
RUN mkdir -p /app/app/static/uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## 2. `requirements.txt`

```txt
Flask==2.3.3
Flask-Login==0.6.2
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Werkzeug==2.3.7
gunicorn==21.2.0
python-dotenv==1.0.0
reportlab==4.0.4
Pillow==10.0.0
email-validator==2.0.0
```

## 3. `.env.example` (rename to `.env` for local development; Railway will use its own environment variables)

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:////app/instance/appraisal.db
# For local development use: sqlite:///appraisal.db
```

## 4. `.dockerignore`

```dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.env
.venv
venv
ENV
instance/*.db
.git
.gitignore
README.md
.vscode
*.log
*.sqlite
*.sqlite3
```

## 5. `README.md` (Comprehensive – copy the full content from the previous message, but I'll repeat it here for convenience)

```markdown
# Edo State Government Performance Appraisal System

A comprehensive Flask-based web application for managing employee performance appraisals for the Edo State Government Civil Service Commission.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Test Users](#test-users)
- [Workflow Guide](#workflow-guide)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 System Overview

The system manages two distinct performance appraisal modules:

### Leg 1: Gen 79A Annual Performance Appraisal
- Traditional single annual report
- Two-level approval workflow (Reporting Officer → Countersigning Officer)
- A-F grading scale with numerical equivalents
- QR code verification for report authenticity
- PDF generation with Edo State Government branding

### Leg 2: Quarterly Performance Appraisal System
- Continuous performance tracking across 4 quarters
- SMART goal setting and approval workflow
- End-of-year appraisal with 0-80 scoring system
- Three-level workflow (Officer → Reporting Officer → Countersigning Officer)
- Officer response mechanism for assessment disagreements

## ✨ Features

- **Authentication & Authorization**: Role-based access control (Admin, Officer, Reporting Officer, Countersigning Officer, HR)
- **Report Management**: Create, edit, submit, and track performance reports
- **Workflow Engine**: Automated routing through approval chains
- **Audit Trail**: Comprehensive logging of all system actions
- **PDF Generation**: Professional report export with QR codes
- **Admin Dashboard**: Full control over users, reports, and system settings
- **Background Logo Settings**: Customizable watermark logo
- **Bulk User Upload**: CSV import for user management
- **Email Notifications**: (Configured separately)

## 📂 Project Structure

```
performance_appraisal/
├── run.py                                      # Application entry point
├── config.py                                   # Configuration settings
├── requirements.txt                            # Python dependencies
├── .env                                        # Environment variables
│
├── app/
│   ├── __init__.py                             # Flask app factory
│   ├── extensions.py                           # SQLAlchemy, LoginManager
│   │
│   ├── models/                                 # Database models
│   │   ├── user.py                             # User model (roles, auth)
│   │   ├── officer.py                          # Officer profile model
│   │   ├── performance_report.py               # Gen 79A report model
│   │   ├── assessment.py                       # Performance grading model
│   │   ├── quarterly_plan.py                   # Quarterly goals & appraisals
│   │   ├── audit_log.py                        # System audit trail
│   │   └── system_settings.py                  # Background logo settings
│   │
│   ├── routes/                                 # Blueprint routes
│   │   ├── auth/                               # Login, logout, auth
│   │   ├── reports/                            # Gen 79A report CRUD
│   │   ├── admin/                              # Admin management
│   │   ├── officers/                           # Officer profiles
│   │   ├── assessments/                        # Assessment grading
│   │   └── quarterly/                          # Quarterly system
│   │
│   ├── templates/                              # HTML templates (46 files)
│   │   ├── base.html                           # Base template
│   │   ├── dashboard.html                      # Gen 79A dashboard
│   │   ├── login.html                          # Login page
│   │   ├── admin/                              # Admin panel templates
│   │   ├── quarterly/                          # Quarterly system templates
│   │   └── reports/                            # Report templates
│   │
│   ├── static/                                 # Static files
│   ├── utils/                                  # Utility modules
│   │   ├── pdf_generator.py                    # Gen 79A PDF generation
│   │   ├── pdf_quarterly.py                    # Quarterly PDF generation
│   │   ├── audit_logger.py                     # Audit logging
│   │   └── unified_audit_logger.py             # Unified audit logging
│   │
│   └── services/                               # Business logic services
│
├── Dockerfile                                  # Docker configuration
├── docker-compose.yml                          # Docker Compose (optional)
├── .dockerignore                               # Docker ignore file
│
└── instance/
    └── appraisal.db                            # SQLite database file
```

## 🚀 Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/Franie83/Performance-Appraisal-.git
cd performance_appraisal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()

# Run the application
python run.py
```

### Docker Deployment

```bash
# Build the image
docker build -t performance-appraisal .

# Run the container
docker run -p 5000:5000 performance-appraisal
```

### Railway Deployment

1. Push code to GitHub repository
2. Create a new project on Railway
3. Connect your GitHub repository
4. Railway will automatically detect the Dockerfile
5. Add the following environment variables:
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production
   - `DATABASE_URL`: SQLite path
6. Deploy

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///appraisal.db
```

## 👥 Test Users

| Username | Password | Role | Department/Ministry |
|----------|----------|------|---------------------|
| admin | admin123 | ADMIN | - |
| john_doe | password123 | OFFICER | Digital Economy and Innovation |
| jane_smith | password123 | OFFICER | - |
| reporting_officer | password123 | REPORTING_OFFICER | Digital Economy and Innovation |
| countersigning_officer | password123 | COUNTERSIGNING_OFFICER | Ministry of Digital Economy |
| permanent_secretary | password123 | COUNTERSIGNING_OFFICER | - |
| hr_officer | password123 | HR | - |
| cs_officer | password123 | COUNTERSIGNING_OFFICER | - |

## 📋 Workflow Guide

### Gen 79A Annual Appraisal Workflow

1. **Officer** creates and submits report (Status: DRAFT → SUBMITTED)
2. **Reporting Officer** reviews and approves/returns (Status: SUBMITTED → APPROVED/MODIFIED)
3. **Countersigning Officer** final approves (Status: APPROVED → FINALIZED)

### Quarterly Appraisal Workflow

1. **Officer** creates SMART goals (Status: DRAFT)
2. **Officer** submits goals for approval
3. **Reporting Officer** approves goals
4. **Countersigning Officer** final approves goals
5. **Officer** submits quarterly reviews
6. **Reporting Officer** assesses reviews
7. **Countersigning Officer** finalizes reviews
8. **Officer** completes yearly self-assessment
9. **Reporting Officer** evaluates and sends for response
10. **Officer** agrees/disagrees with assessment
11. **Countersigning Officer** finalizes yearly appraisal

## 🔧 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Reports (Gen 79A)
- `GET /reports/dashboard` - Main dashboard
- `GET /reports/my-reports` - User's reports
- `POST /reports/create` - Create report
- `GET /reports/view/<int:report_id>` - View report
- `POST /reports/submit/<int:report_id>` - Submit for approval
- `GET /reports/export-pdf/<int:report_id>` - Download PDF

### Quarterly System
- `GET /quarterly/dashboard` - Quarterly dashboard
- `POST /quarterly/plan-goal` - Create SMART goal
- `POST /quarterly/submit-goal/<int:goal_id>` - Submit goal
- `POST /quarterly/approve-goal/<int:goal_id>` - Approve goal
- `POST /quarterly/quarterly-review/<int:quarter>` - Submit quarterly review
- `POST /quarterly/yearly-appraisal` - Submit yearly appraisal
- `GET /quarterly/respond-appraisal/<int:appraisal_id>` - Officer response page
- `GET /quarterly/ps-review/<int:appraisal_id>` - CS/PS review page

### Admin
- `GET /admin/manage-users` - User management
- `GET /admin/manage-officers` - Officer profile management
- `GET /admin/manage-reports` - Report management
- `POST /admin/create-user` - Create user
- `PUT /admin/update-user/<int:user_id>` - Update user
- `DELETE /admin/delete-user/<int:user_id>` - Delete user
- `GET /admin/system-stats` - System statistics
- `GET /quarterly/admin/audit-trail` - Audit trail viewer

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Database locked | Delete `app/__pycache__` folder |
| Modal not opening | Add `data-bs-backdrop="static"` to modal |
| PDF generation fails | Run `pip install reportlab` |
| Circular import error | Move imports to bottom of `__init__.py` |
| Edit user hangs | Check JavaScript event listener binding |
| Audit trail not showing | Run `python add_module_column.py` |

### Database Migration

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Reset Database

```bash
rm instance/appraisal.db
python run.py  # Database will be recreated
```

## 📜 License

© 2024 Edo State Government - Civil Service Commission. All Rights Reserved.

---

**For support, contact the IT department or raise an issue on GitHub.**
```

## 6. (Optional) `docker-compose.yml` – for local multi-container testing

```yaml
version: '3.8'

services:
  appraisal:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=production
      - SECRET_KEY=change-this-in-production
    volumes:
      - ./instance:/app/instance
    restart: unless-stopped
```

## How to create these files in VS Code

1. Open your project folder in VS Code.
2. Create a new file (Ctrl+N) and save with the exact filename (e.g., `Dockerfile`, `requirements.txt`, etc.).
3. Copy the corresponding content from above into the file.
4. Save.

After creating these files, commit and push to GitHub. Railway will automatically build and deploy the app using the Dockerfile.

> **Important**: Ensure you have a `run.py` entry point that creates the Flask app. If your `run.py` does not expose a variable named `app`, adjust the CMD line accordingly (e.g., `CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]`). Based on your existing `run.py`, it likely creates the app with `create_app()`. If so, change the CMD to:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "/app", "run:app"]
```

If your `run.py` uses `app = create_app()` and then `if __name__ == '__main__': app.run()`, it should work as is. The above Dockerfile assumes `app` is the WSGI callable. If `run.py` does not define `app`, you can modify it to: 

```python
from app import create_app
app = create_app()
```

Then `run:app` will work.