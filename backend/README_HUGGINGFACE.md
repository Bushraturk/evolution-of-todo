---
title: Todo App Backend API
emoji: ✅
colorFrom: purple
colorTo: violet
sdk: docker
pinned: false
license: mit
---

# Todo App Backend API

FastAPI backend for the Evolution of Todo application with user authentication and task management.

## 🚀 Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **Task Management**: Full CRUD operations for tasks
- **Category System**: Organize tasks by categories
- **Advanced Filtering**: Search, filter by status/priority/category, and sort tasks
- **PostgreSQL Database**: Production-ready with Neon DB
- **RESTful API**: Clean API design with automatic documentation

## 📚 API Documentation

Visit `/docs` for interactive Swagger UI documentation.

## 🔧 Environment Variables

This Space requires the following secrets (configure in Settings → Repository secrets):

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `JWT_SECRET` | Secret key for JWT token signing (32+ chars) | Generate with crypto.randomBytes(32) |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://your-app.vercel.app,http://localhost:3000` |
| `DEBUG` | Debug mode (set to `false` in production) | `false` |

## 🔗 Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks` - List all tasks (with filtering, search, sort)
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/toggle` - Toggle task completion

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create new category

### Health
- `GET /health` - Health check endpoint

## 🧪 Testing the API

### 1. Health Check
```bash
curl https://YOUR-SPACE-URL.hf.space/health
```

### 2. Register User
```bash
curl -X POST https://YOUR-SPACE-URL.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'
```

### 3. Create Task
```bash
curl -X POST https://YOUR-SPACE-URL.hf.space/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title":"Test Task","description":"Testing API","priority":"high"}'
```

## 🏗️ Tech Stack

- **Framework**: FastAPI 0.109+
- **ORM**: SQLModel 0.0.14+
- **Database**: PostgreSQL (Neon DB)
- **Authentication**: JWT with PyJWT
- **Password Hashing**: Passlib with bcrypt
- **Server**: Uvicorn

## 📦 Deployment

This Space uses Docker for deployment. The Dockerfile:
1. Uses Python 3.13 slim image
2. Installs system dependencies (gcc, postgresql-client)
3. Installs Python dependencies from requirements.txt
4. Copies application code
5. Runs on port 7860 (Hugging Face default)

## 🔒 Security

- Passwords are hashed with bcrypt
- JWT tokens expire after 7 days
- CORS is configured to allow only specified origins
- SQL injection protection via SQLModel ORM
- Environment variables for sensitive data

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

This is part of the Evolution of Todo project. For issues or contributions, visit the main repository.

## 🔗 Related Links

- Frontend Application: [Add your Vercel URL here]
- Main Repository: https://github.com/Bushraturk/evolution-of-todo
- API Documentation: https://YOUR-SPACE-URL.hf.space/docs
