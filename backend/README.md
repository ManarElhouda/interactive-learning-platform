# Interactive Learning Platform - Backend

A clean, modular FastAPI backend for the Interactive Learning Platform full-stack project. Designed for team development with a simple, scalable structure.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or pip3

### Setup

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Docs (Swagger): `http://localhost:8000/api/docs`
   - API Redoc: `http://localhost:8000/api/redoc`

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
│
└── app/
    ├── __init__.py
    ├── config.py          # Configuration from environment
    ├── middleware.py      # CORS and security middleware
    ├── schemas.py         # Pydantic models (data validation)
    │
    ├── api/
    │   ├── __init__.py
    │   └── routes/
    │       ├── __init__.py
    │       ├── health.py  # Health check endpoint
    │       └── lessons.py # Lesson CRUD endpoints
    │
    ├── models/
    │   ├── __init__.py
    │   └── lesson.py      # SQLAlchemy database models
    │
    ├── services/
    │   ├── __init__.py
    │   └── lesson_service.py  # Business logic layer
    │
    ├── database/
    │   ├── __init__.py
    │   └── connection.py   # Database setup and session management
    │
    └── utils/
        └── __init__.py     # Utility functions (add as needed)
```

## 🏗️ Architecture

This backend follows a clean, layered architecture:

- **Routes** (`api/routes/`): HTTP endpoint handlers
- **Schemas** (`schemas.py`): Request/response validation (similar to Zod in frontend)
- **Services** (`services/`): Business logic and data processing
- **Models** (`models/`): Database models (SQLAlchemy)
- **Database** (`database/`): Connection and session management
- **Config** (`config.py`): Environment configuration

## 🔌 Frontend Integration

The backend is CORS-enabled and compatible with the TanStack React Router frontend:

- CORS headers are pre-configured for `http://localhost:5173` (frontend dev server)
- All API endpoints follow RESTful conventions
- Error responses are consistent and frontend-friendly
- Supports frontend-initiated requests with proper headers

## 📚 API Endpoints

### Health Check
- `GET /api/` - API status and version

### Lessons
- `GET /api/lessons` - List all lessons (with pagination)
- `GET /api/lessons/{id}` - Get a specific lesson
- `POST /api/lessons` - Create a new lesson
- `PUT /api/lessons/{id}` - Update a lesson
- `DELETE /api/lessons/{id}` - Delete a lesson

## 🛠️ Development

### Adding a New Feature

1. **Create a new route** in `app/api/routes/`:
   ```python
   # app/api/routes/my_feature.py
   from fastapi import APIRouter
   from app.schemas import MySchema

   router = APIRouter()

   @router.get("")
   async def get_my_feature():
       return {"message": "Hello"}
   ```

2. **Update the router** in `app/api/routes/__init__.py`:
   ```python
   from .my_feature import router as my_feature_router
   
   api_router.include_router(
       my_feature_router, 
       prefix="/my-feature", 
       tags=["my-feature"]
   )
   ```

3. **Add schema validation** to `app/schemas.py`

4. **Create a service** in `app/services/` if business logic is needed

### Testing (Optional)

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

Run tests:
```bash
pytest
```

## 🌍 Environment Variables

See `.env.example` for all available options:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | App environment (development/staging/production) |
| `DEBUG` | `True` | Enable debug mode |
| `PORT` | `8000` | Server port |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS |
| `DATABASE_URL` | `sqlite:///./app.db` | Database connection string |

## 🤝 Team Development

### Best Practices

1. **Feature branches**: Create a branch for each feature
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Code style**: Keep it simple and consistent
   - Use type hints
   - Document functions with docstrings
   - Follow PEP 8

3. **Commit messages**: Be descriptive
   ```bash
   git commit -m "feat: add lesson filtering by difficulty"
   ```

4. **Testing before push**: Always test your changes
   ```bash
   uvicorn main:app --reload
   ```

### Collaboration Tips

- Discuss new features in PRs before merging
- Keep the main branch stable and deployable
- Document breaking changes in commit messages
- Update `.env.example` if adding new environment variables

## 📝 Database

### Default: SQLite (Development)

For development, SQLite is used by default (`app.db`). Tables are auto-created on startup.

### Production: PostgreSQL

Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/learning_platform
```

Then install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

## 🚀 Deployment

This backend is designed for easy deployment:

- Environment-based configuration
- Database agnostic (SQLite → PostgreSQL)
- CORS pre-configured
- Built with FastAPI (production-ready)

Popular deployment options:
- **Heroku**: `Procfile` ready
- **Railway**: Simple GitHub integration
- **Render**: Free tier available
- **AWS/Azure**: Standard FastAPI deployment

## 📖 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Uvicorn Server](https://www.uvicorn.org/)

## 📄 License

This project is part of the Interactive Learning Platform. See LICENSE file for details.
