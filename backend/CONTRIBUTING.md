# Contributing to the Backend

Welcome to the team! This guide will help you get started with backend development.

## 🎯 Before You Start

1. **Read the README.md** - Understand the project structure
2. **Set up your environment** - Follow the Quick Start section
3. **Verify it works** - Run `uvicorn main:app --reload` and check `/api/docs`

## 🔄 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

### 2. Make Your Changes
- Create routes, services, models, schemas as needed
- Refer to [FEATURE_EXAMPLE.md](FEATURE_EXAMPLE.md) for the pattern
- Keep the structure clean and organized

### 3. Test Locally
```bash
# Run the server
uvicorn main:app --reload

# Check your endpoints at http://localhost:8000/api/docs
# Test with the interactive Swagger UI
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: describe what you added"
# Examples:
# git commit -m "feat: add user authentication routes"
# git commit -m "fix: fix lesson filtering by difficulty"
# git commit -m "docs: update README with new endpoints"
```

### 5. Push and Create a Pull Request
```bash
git push origin feature/your-feature-name
```

Then open a PR on GitHub with:
- Clear title describing the change
- Description of what was added/fixed
- Any important notes for reviewers

## 📋 Code Style

We follow simple Python conventions:

### Type Hints (Required)
```python
# ✓ Good
def get_lesson(lesson_id: int) -> Optional[Lesson]:
    pass

# ✗ Avoid
def get_lesson(lesson_id):
    pass
```

### Docstrings (Required for Public Functions)
```python
def create_lesson(lesson_data: LessonCreate) -> Lesson:
    """Create a new lesson in the database."""
    pass
```

### Naming
```python
# ✓ Use clear names
def fetch_user_lessons()
lesson_count = 5
USER_ROLE_ADMIN = "admin"

# ✗ Avoid abbreviations
def f_u_l()
lc = 5
URA = "admin"
```

## 🏗️ Adding a New Endpoint

Follow this pattern:

1. **Add schema** → `app/schemas.py`
2. **Add model** → `app/models/new_feature.py`
3. **Add service** → `app/services/new_feature_service.py`
4. **Add route** → `app/api/routes/new_feature.py`
5. **Register route** → Update `app/api/routes/__init__.py`

See [FEATURE_EXAMPLE.md](FEATURE_EXAMPLE.md) for details.

## 🐛 Debugging

### Access API Documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### Check Logs
```bash
# The terminal running uvicorn shows all requests and errors
# Look for:
# - Request method and path
# - Response status codes
# - Error messages
```

### Database Issues
```bash
# SQLite database is created at app.db
# To reset: simply delete app.db and restart the server
rm app.db
uvicorn main:app --reload
```

### Use Python Debugger
```python
# Add this to your code:
import pdb; pdb.set_trace()

# Or with print statements:
print("DEBUG:", variable_name)
```

## 📦 Environment Variables

If you add new environment variables:

1. **Add to `.env.example`** with a comment explaining it
2. **Add to `app/config.py`** in the Settings class
3. **Document in README.md** if it's user-facing

Example:
```python
# app/config.py
api_key: str = os.getenv("MY_API_KEY", "default_value")

# .env.example
# MY_API_KEY=your_key_here
```

## 🤝 Common Tasks

### Want to add a database table?
1. Create a new file in `app/models/`
2. Define the SQLAlchemy model
3. It will automatically create on server restart

### Want to add a service method?
1. Add the method to the appropriate service in `app/services/`
2. Use it in your route handler

### Want to add validation?
1. Add a Pydantic schema to `app/schemas.py`
2. Use it as a route parameter: `@router.post("/", response_model=MySchema)`

## 🚨 Common Mistakes

```python
# ❌ Don't create multiple SessionLocal instances
service = LessonService()  # Creates its own session
service2 = LessonService()  # Another session

# ✓ Do reuse sessions when needed (advanced)
db = SessionLocal()
service = LessonService(db)

# ❌ Don't forget to commit database changes
db.add(new_item)
# Missing: db.commit()

# ✓ Service handles this
service.create_item(data)  # Service commits

# ❌ Don't hardcode values
DATABASE_URL = "postgresql://localhost/db"

# ✓ Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
```

## 📝 Before Submitting PR

- [ ] Code follows style guidelines (type hints, docstrings)
- [ ] Tested locally with `uvicorn main:app --reload`
- [ ] Checked endpoints in Swagger UI (`/api/docs`)
- [ ] `.env.example` updated if needed
- [ ] No print statements left in code (use logging if needed)
- [ ] Commit messages are clear

## 💬 Questions?

If you're unsure about something:
1. Check [FEATURE_EXAMPLE.md](FEATURE_EXAMPLE.md)
2. Look at existing similar code
3. Ask in the team chat or create a GitHub Discussion

## ✨ Tips for Success

- **Small commits**: Make focused commits that do one thing
- **Test as you go**: Don't wait until the end to test
- **Read the code**: Understanding existing code helps you add better code
- **Ask questions**: It's better to ask than to guess wrong
- **Keep it simple**: Simple code is easier to maintain and debug

Welcome to the team! 🚀
