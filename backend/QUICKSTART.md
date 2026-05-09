# Quick Reference - Backend Setup & Usage

## 🚀 One-Time Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

## ▶️ Start Development Server
```bash
uvicorn main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 📁 File Organization

```
What's inside:
├── main.py                    ← Start here
├── app/
│   ├── config.py             ← Environment settings
│   ├── middleware.py         ← CORS setup
│   ├── schemas.py            ← Data validation (like Zod)
│   ├── api/routes/           ← Your endpoints
│   ├── models/               ← Database tables
│   ├── services/             ← Business logic
│   ├── database/             ← DB connection
│   └── utils/                ← Helpers
├── requirements.txt          ← Dependencies
├── .env.example              ← Config template
├── CONTRIBUTING.md           ← Team guide
├── FEATURE_EXAMPLE.md        ← How to add features
└── README.md                 ← Full documentation
```

## ✨ Adding a Feature (3 Steps)

1. **Define schema** → Add to `app/schemas.py`
2. **Create service** → New file in `app/services/`
3. **Add route** → New file in `app/api/routes/`, then register in `app/api/routes/__init__.py`

See `FEATURE_EXAMPLE.md` for full example.

## 🔗 Frontend Compatibility

- ✓ CORS enabled for `http://localhost:5173`
- ✓ API follows REST conventions
- ✓ Pydantic validation (similar to Zod)
- ✓ Standard JSON responses

## 💾 Database

- Default: SQLite (`app.db`)
- Auto-initializes tables on startup
- To reset: Delete `app.db` and restart

## 📚 Current Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root info |
| GET | `/api/` | Health check |
| GET | `/api/lessons` | List lessons |
| GET | `/api/lessons/{id}` | Get lesson |
| POST | `/api/lessons` | Create lesson |
| PUT | `/api/lessons/{id}` | Update lesson |
| DELETE | `/api/lessons/{id}` | Delete lesson |

## 🛠️ Development Tools

- **Hot reload**: Built into uvicorn (auto-restarts on code changes)
- **Interactive docs**: Swagger at `/api/docs`
- **Database queries**: Check `app.db` with SQLite tools
- **Debugging**: Add `import pdb; pdb.set_trace()` in code

## 📋 Before Git Commit

- [ ] Code has type hints
- [ ] Functions have docstrings  
- [ ] Tested in browser at `/api/docs`
- [ ] Updated `.env.example` if needed
- [ ] Clear commit message

## 🤔 Common Commands

```bash
# Install new package
pip install package-name
pip freeze > requirements.txt

# Format code
black .

# Run tests (after setup with -dev)
pytest

# Check specific endpoint
curl http://localhost:8000/api/
```

## 📞 File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app setup & startup |
| `config.py` | Loads env vars, app settings |
| `middleware.py` | CORS, security headers |
| `schemas.py` | Pydantic validation models |
| `app/api/routes/` | HTTP handlers |
| `app/models/` | SQLAlchemy ORM models |
| `app/services/` | Business logic & DB queries |
| `app/database/connection.py` | DB setup |

---

**Next Step**: Run the server and check `/api/docs` to explore the API! 🎉
