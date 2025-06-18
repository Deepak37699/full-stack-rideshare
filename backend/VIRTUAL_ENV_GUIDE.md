# Python Virtual Environment Setup for RideShare Backend

## Current Status

✅ Virtual environment is already created and configured by `uv`
✅ Location: `backend/.venv/`
✅ Python version: 3.11.13
✅ All dependencies installed

## Working with the Virtual Environment

### Method 1: Using uv (Recommended)

```bash
# Navigate to backend directory
cd backend

# Run Python commands through uv (automatically uses virtual environment)
uv run python manage.py runserver
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Install new packages
uv add package_name

# See installed packages
uv pip list
```

### Method 2: Manual Activation (Windows)

```cmd
# Navigate to backend directory
cd backend

# Activate virtual environment
.venv\Scripts\activate

# Now you can use python directly
python manage.py runserver
python manage.py migrate

# Deactivate when done
deactivate
```

### Method 3: Manual Activation (Git Bash/PowerShell)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source .venv/Scripts/activate

# Use python directly
python manage.py runserver

# Deactivate when done
deactivate
```

## VS Code Integration

VS Code should automatically detect the virtual environment. You can also:

1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose: `backend/.venv/Scripts/python.exe`

## Environment Variables

Create a `.env` file in the backend directory with:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Quick Commands

- **Start Django server**: `uv run python manage.py runserver`
- **Make migrations**: `uv run python manage.py makemigrations`
- **Apply migrations**: `uv run python manage.py migrate`
- **Create superuser**: `uv run python manage.py createsuperuser`
- **Django shell**: `uv run python manage.py shell`

The virtual environment is ready for development! 🚀
