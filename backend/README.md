# CampusCare - FastAPI Backend with Supabase Integration

This is the backend service for **CampusCare: Web-Based Campus Asset Reporting and Ticketing System**, built with **FastAPI** and connected to **Supabase** (PostgreSQL & Supabase Auth).

---

## 🗄️ Database Schema Overview

The backend integrates with three core tables linked to Supabase Auth (`auth.users.id`):

1. **`public.users`** (Students & Faculty):
   - `id` (UUID, Foreign Key to `auth.users(id)`)
   - `school_id` (Unique text)
   - `first_name`, `middle_name`, `last_name`
   - `user_type` (`student` or `faculty`)
   - `created_at` (Timestamp)

2. **`public.maintenance_personnel`** (Maintenance Staff):
   - `id` (UUID, Foreign Key to `auth.users(id)`)
   - `school_id` (Unique text, optional)
   - `first_name`, `middle_name`, `last_name`
   - `email` (Unique text)
   - `department` (e.g., Physical Plant, IT, Facilities)
   - `maintenance_category` (e.g., Electrical, Plumbing, HVAC, Carpentry)
   - `employment_status` (`pending`, `active`, `inactive`)
   - `created_at` (Timestamp)

3. **`public.admin`** (System Administrators):
   - `id` (UUID, Foreign Key to `auth.users(id)`)
   - `school_id` (Unique text)
   - `first_name`, `middle_name`, `last_name`
   - `email` (Unique text)
   - `password` (Text, optional)
   - `role` (`admin`)
   - `created_at` (Timestamp)

---

## 🚀 Quick Start Guide

### 1. Set Up Database in Supabase

1. Open your [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to **SQL Editor** -> **New Query**.
3. Copy the contents of [`backend/supabase_schema.sql`](file:///home/angelo/Documents/Personal%20Project/CampusCare/backend/supabase_schema.sql) and run it.
   - This creates tables, constraints, indexes, and Row-Level Security (RLS) policies.

### 2. Configure Environment Variables

Open or copy `backend/.env.example` to `backend/.env`:

```bash
cp .env.example .env
```

Set your credentials from **Supabase Dashboard** -> **Project Settings** -> **API**:

```env
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=<your-anon-public-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-secret-key>
SUPABASE_JWT_SECRET=<your-jwt-secret>
```

### 3. Activate Virtual Environment & Run Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API Base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📡 API Endpoints Summary

### 🔐 Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Log in with email & password; returns JWT and user profile |
| `POST` | `/api/v1/auth/register/user` | Register student or faculty |
| `POST` | `/api/v1/auth/register/maintenance` | Register maintenance staff (starts with `pending` status) |
| `POST` | `/api/v1/auth/register/admin` | Register administrator |
| `GET` | `/api/v1/auth/me` | Fetch profile & role of current authenticated user |

### 👥 Users: Students & Faculty (`/api/v1/users`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/users/` | List users (supports `user_type`, `search`, pagination) |
| `GET` | `/api/v1/users/{id}` | Get user by UUID |
| `GET` | `/api/v1/users/by-school-id/{school_id}` | Get user by school ID |
| `POST` | `/api/v1/users/` | Create user profile (Admin) |
| `PUT` | `/api/v1/users/{id}` | Update profile (Owner or Admin) |
| `DELETE` | `/api/v1/users/{id}` | Delete profile (Admin) |

### 🛠️ Maintenance Personnel (`/api/v1/maintenance`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/maintenance/` | List staff (filters: `department`, `maintenance_category`, `employment_status`) |
| `GET` | `/api/v1/maintenance/{id}` | Get maintenance staff by UUID |
| `PUT` | `/api/v1/maintenance/{id}` | Update staff profile |
| `PATCH`| `/api/v1/maintenance/{id}/status` | Approve or change employment status (`pending`/`active`/`inactive`) (Admin) |
| `DELETE`| `/api/v1/maintenance/{id}` | Remove maintenance personnel (Admin) |

### 🛡️ Administrators (`/api/v1/admins`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admins/` | List administrators |
| `GET` | `/api/v1/admins/{id}` | Get admin by UUID |
| `GET` | `/api/v1/admins/by-school-id/{school_id}` | Get admin by school ID |
| `PUT` | `/api/v1/admins/{id}` | Update admin profile |
| `DELETE`| `/api/v1/admins/{id}` | Delete admin profile |

---

## 🧪 Running Automated Tests

```bash
cd backend
source venv/bin/activate
pytest tests/
```
