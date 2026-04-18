
<div align="center">
# 🚀 Fundly — Backend API

**A powerful, production-ready crowdfunding REST API built with Django & Django REST Framework**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

</div>
---


---

## 📋 Table of Contents

* [Overview](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-overview)
* [Features](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-features)
* [Tech Stack](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-tech-stack)
* [Project Structure](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-project-structure)
* [Getting Started](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-getting-started)
* [Environment Variables](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-environment-variables)
* [API Reference](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-api-reference)
* [Authentication Flow](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-authentication-flow)
* [Data Models](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-data-models)
* [Deployment](https://claude.ai/chat/0f3f1d8f-fed6-441d-afc0-a28c0f91a290#-deployment)

---

## 🌟 Overview

**Fundly** is a full-featured crowdfunding platform backend that allows users to create projects, receive donations, engage with comments, and rate campaigns. It is built for scale, with clean architecture, JWT-based authentication, email verification, and optional Cloudinary media hosting.

---

## ✨ Features

| Feature                     | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| 🔐**Auth & Security** | JWT access/refresh tokens, token blacklisting, email verification           |
| 👤**User Management** | Custom user model with email-based auth, profile management, password reset |
| 📁**Projects**        | Full CRUD, categories, tags, image uploads, featured & top-rated listings   |
| 💰**Donations**       | Per-project donations with live progress tracking                           |
| 💬**Comments**        | Nested comments (1-level deep replies) with author info                     |
| ⭐**Ratings**         | 1–5 star project ratings with average aggregation                          |
| 🚩**Reports**         | Flag projects or comments for spam/inappropriate content                    |
| 🔍**Search & Filter** | Full-text search, category/tag filtering, ordering                          |
| 📧**Email**           | Transactional emails via SendGrid (activation & password reset)             |
| ☁️**Media**         | Local filesystem or Cloudinary (toggle via env var)                         |
| 🌐**CORS**            | Configured for React/Vite frontends                                         |

---

## 🛠 Tech Stack

* **Framework:** Django 6.0 + Django REST Framework 3.17
* **Database:** PostgreSQL (via `psycopg2-binary`)
* **Auth:** `djangorestframework-simplejwt` with token blacklisting
* **Email:** `django-anymail` + SendGrid
* **Media:** Pillow + optional `django-cloudinary-storage`
* **Static Files:** WhiteNoise
* **Filtering:** `django-filter`
* **Config:** `python-decouple`
* **Deployment:** Gunicorn + Render-ready

---

## 🗂 Project Structure

```
Fundly-Backend/
│
├── config/                  # Django project settings & routing
│   ├── settings.py          # All settings (env-driven)
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # Custom user model & auth
│   ├── models.py            # CustomUser (email-based)
│   ├── serializers.py       # Register, login, profile, password
│   ├── views.py             # Auth endpoints
│   ├── urls.py
│   └── utils.py             # Email sending helpers
│
├── projects/                # Crowdfunding projects
│   ├── models.py            # Project, Category, Tag, ProjectImage
│   ├── serializers.py       # List, detail, write serializers
│   ├── views.py             # CRUD + featured/top-rated/similar
│   ├── filters.py
│   └── permissions.py
│
├── donations/               # Donation handling
│   ├── models.py            # Donation model
│   ├── serializers.py
│   └── views.py
│
├── comments/                # Project comments & replies
│   ├── models.py            # Comment (self-referencing for replies)
│   ├── serializers.py
│   └── views.py
│
├── ratings/                 # Project star ratings
│   ├── models.py            # Rating (1–5, one per user per project)
│   ├── serializers.py
│   └── views.py
│
├── reports/                 # Flagging content
│   ├── models.py            # Report (project or comment)
│   ├── serializers.py
│   └── views.py
│
├── manage.py
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.12+
* PostgreSQL 14+
* (Optional) A [Cloudinary](https://cloudinary.com/) account for media hosting
* (Optional) A [SendGrid](https://sendgrid.com/) API key for emails

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/fundly-backend.git
cd fundly-backend
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your values — see Environment Variables below
```

### 5. Create the Database

```bash
psql -U postgres -c "CREATE DATABASE crowdfunding_db;"
```

### 6. Apply Migrations

```bash
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at  **`http://localhost:8000`** .

---

## 🔑 Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=crowdfunding_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=hello@yourapp.com

# Frontend (used in activation & reset email links)
FRONTEND_URL_DEPLOY=http://localhost:5173

# Media Storage (set to True to use Cloudinary)
USE_CLOUDINARY=False
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 📡 API Reference

Base URL: `/api/`

### 🔐 Authentication — `/api/auth/`

| Method        | Endpoint                                        | Auth     | Description                      |
| ------------- | ----------------------------------------------- | -------- | -------------------------------- |
| `POST`      | `/auth/register/`                             | ❌       | Register a new user              |
| `GET`       | `/auth/activate/<uid>/<token>/`               | ❌       | Verify email address             |
| `POST`      | `/auth/login/`                                | ❌       | Login & receive JWT tokens       |
| `POST`      | `/auth/logout/`                               | ✅       | Logout & blacklist refresh token |
| `POST`      | `/auth/token/refresh/`                        | ❌       | Refresh access token             |
| `GET/PATCH` | `/auth/profile/`                              | ✅       | View or update profile           |
| `DELETE`    | `/auth/profile/delete/`                       | ✅       | Delete account                   |
| `POST`      | `/auth/password/change/`                      | ✅       | Change password                  |
| `POST`      | `/auth/password/reset/`                       | ❌       | Request password reset email     |
| `POST`      | `/auth/password/reset/confirm/<uid>/<token>/` | ❌       | Set new password                 |
| `GET`       | `/auth/users/`                                | 🔑 Admin | List all users                   |

### 📁 Projects — `/api/projects/`

| Method        | Endpoint                    | Auth     | Description                                  |
| ------------- | --------------------------- | -------- | -------------------------------------------- |
| `GET`       | `/projects/`              | ❌       | List all projects (filter, search, paginate) |
| `POST`      | `/projects/`              | ✅       | Create a new project                         |
| `GET`       | `/projects/<id>/`         | ❌       | Retrieve project details                     |
| `PUT/PATCH` | `/projects/<id>/`         | ✅ Owner | Update project                               |
| `POST`      | `/projects/<id>/cancel/`  | ✅ Owner | Cancel project (if progress < 25%)           |
| `GET`       | `/projects/<id>/similar/` | ❌       | Get similar projects by tags                 |
| `GET`       | `/projects/featured/`     | ❌       | List featured projects                       |
| `GET`       | `/projects/top-rated/`    | ❌       | List top-rated active projects               |
| `GET`       | `/projects/categories/`   | ❌       | List all categories                          |
| `POST`      | `/projects/categories/`   | 🔑 Admin | Create a category                            |
| `GET`       | `/projects/tags/`         | ❌       | List all tags                                |
| `POST`      | `/projects/tags/`         | 🔑 Admin | Create a tag                                 |

**Query Parameters for `GET /projects/`:**

```
?search=keyword        # Search title, description, tags
?category=slug         # Filter by category slug
?tag=slug              # Filter by tag slug
?owner=user_id         # Filter by owner
```

### 💰 Donations — `/api/donations/`

| Method   | Endpoint                             | Auth | Description                         |
| -------- | ------------------------------------ | ---- | ----------------------------------- |
| `POST` | `/donations/donate/<project_id>/`  | ✅   | Make a donation                     |
| `GET`  | `/donations/project/<project_id>/` | ❌   | Get project donation details        |
| `GET`  | `/donations/my-donations/`         | ✅   | Get current user's donation history |

### 💬 Comments — `/api/comments/`

| Method     | Endpoint                            | Auth     | Description                 |
| ---------- | ----------------------------------- | -------- | --------------------------- |
| `GET`    | `/comments/project/<project_id>/` | ❌       | List comments for a project |
| `POST`   | `/comments/project/<project_id>/` | ✅       | Post a comment              |
| `POST`   | `/comments/<comment_id>/reply/`   | ✅       | Reply to a comment          |
| `PATCH`  | `/comments/<comment_id>/`         | ✅ Owner | Edit a comment              |
| `DELETE` | `/comments/<comment_id>/`         | ✅ Owner | Delete a comment            |

### ⭐ Ratings — `/api/ratings/`

| Method   | Endpoint                           | Auth | Description                    |
| -------- | ---------------------------------- | ---- | ------------------------------ |
| `POST` | `/ratings/create/`               | ✅   | Rate a project (1–5 stars)    |
| `GET`  | `/ratings/project/<project_id>/` | ❌   | Get rating stats for a project |

### 🚩 Reports — `/api/reports/`

| Method   | Endpoint              | Auth | Description                          |
| -------- | --------------------- | ---- | ------------------------------------ |
| `POST` | `/reports/create/`  | ✅   | Report a project or comment          |
| `GET`  | `/reports/reasons/` | ❌   | List available report reason choices |

---

## 🔐 Authentication Flow

```
1.  POST /api/auth/register/        → Creates user (is_email_verified=False)
2.  Email sent with activation link
3.  GET  /api/auth/activate/<uid>/<token>/  → Verifies email
4.  POST /api/auth/login/           → Returns { access, refresh }
5.  Include header: Authorization: Bearer <access_token>
6.  POST /api/auth/token/refresh/   → Get new access token
7.  POST /api/auth/logout/          → Blacklists refresh token
```

---

## 🗄 Data Models

### CustomUser

```
email (unique, indexed) | first_name | last_name | phone
profile_picture | date_of_birth | country | bio
is_email_verified | created_at | updated_at
```

### Project

```
owner (FK→User) | title | description | target (decimal)
category (FK→Category) | tags (M2M→Tag) | start_time | end_time
status [active|cancelled|completed] | is_featured
→ computed: progress (%), avg_rating
```

### Donation

```
user (FK→User) | project (FK→Project) | amount | created_at
```

### Comment

```
project (FK→Project) | user (FK→User) | parent (FK→self, nullable)
content | created_at | updated_at
```

### Rating

```
user (FK→User) | project (FK→Project) | value (1–5)
unique_together: (user, project)
```

### Report

```
user (FK→User) | project (FK→Project, nullable) | comment (FK→Comment, nullable)
reason [spam|inappropriate|offensive|other] | created_at
```

---

## ☁️ Deployment

This project is configured for deployment on  **[Render](https://render.com/)** .

### Steps

1. Push your code to GitHub.
2. Create a **Web Service** on Render pointing to your repo.
3. Set **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
4. Set **Start Command:**
   ```bash
   gunicorn config.wsgi:application
   ```
5. Add all required **Environment Variables** in the Render dashboard.

### Production Checklist

* [ ] `DEBUG=False`
* [ ] `SECRET_KEY` is long, random, and secret
* [ ] `ALLOWED_HOSTS` includes your Render domain
* [ ] PostgreSQL add-on configured in Render
* [ ] `USE_CLOUDINARY=True` with valid credentials (recommended for media)
* [ ] `SENDGRID_API_KEY` set for transactional emails
* [ ] `FRONTEND_URL_DEPLOY` points to your deployed frontend

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a pull request

---

<div align="center">
Made with ❤️ by the Fundly Team

</div>
