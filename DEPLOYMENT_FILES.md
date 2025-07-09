# Essential Files for Production Deployment

## Core Application Files (Required)

### Entry Points
- `main.py` - Development server entry point
- `wsgi.py` - **Production WSGI entry point for Gunicorn**
- `gunicorn.conf.py` - Production server configuration

### Application Core  
- `nvcfund-backend/` - **Main application directory**
  - `app_factory.py` - Application factory
  - `config.py` - Configuration classes
  - `modules/` - All 31+ banking modules
  - `templates/` - HTML templates
  - `static/` - CSS, JS, images

### Configuration
- `pyproject.toml` - Python dependencies
- `.env` - Environment variables (create from .env.example)
- `.env.example` - Environment template

## Documentation (Optional but Recommended)
- `docs/PRODUCTION_DEPLOYMENT.md` - Deployment guide
- `docs/README.md` - Documentation index
- `replit.md` - Project overview

## Files to EXCLUDE from Production

### Development Files
- `console_test.py`
- `run_with_console.py` 
- `simple_server_test.py`
- `cookies.txt`

### Cache/Temporary
- `__pycache__/` - Python cache
- `flask_session/` - Development sessions
- `logs/` - Development logs

### Development Assets
- `attached_assets/` - Screenshots/development files
- `scripts/` - Development scripts

## Minimum Production Deployment

For a clean production deployment, you only need:

```
nvc-banking-platform/
├── wsgi.py                 # Production entry point
├── gunicorn.conf.py        # Server config
├── nvcfund-backend/        # Application
├── pyproject.toml          # Dependencies  
├── .env                    # Environment variables
└── docs/                   # Documentation (optional)
```

**Start Command:**
```bash
gunicorn --config gunicorn.conf.py main:app
```

The application will automatically detect the `nvcfund-backend/` directory and load all 31+ banking modules.