# CrowdConnect - PythonAnywhere Deployment Guide

## Step-by-Step Process

### 1. Push Your Code to GitHub

Make sure your project is pushed to your GitHub repository:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

---

### 2. Clone Repo in PythonAnywhere

Open **Bash console** in PythonAnywhere:

```bash
cd ~
git clone https://github.com/Sdngl/Community_event.git
cd Community_event
```

---

### 3. Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.11 CrowdConnect_venv
```

---

### 4. Install Dependencies

```bash
workon CrowdConnect_venv
pip install -r requirements.txt
```

---

### 5. Set Environment Variables

```bash
export FLASK_APP=app.py
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key-here
export DATABASE_URL=sqlite:///event.db
```

---

### 6. Create Database

```bash
flask create-db
```

(Optional) Seed with sample data:

```bash
flask seed-db
```

---

### 7. Configure WSGI File

Go to **Web** tab → Click **WSGI configuration file**

Replace contents with:

```python
import os
import sys

path = '/home/Swowroop/Community_event'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secure-secret-key-here'
os.environ['DATABASE_URL'] = 'sqlite:///event.db'

from app import create_app
application = create_app('production')
```

Click **Save**

---

### 8. Configure Static Files

Go to **Web** tab → Under **Static files**:

| URL        | Directory                                |
| ---------- | ---------------------------------------- |
| `/static/` | `/home/Swowroop/Community_event/static/` |

Click **Enter** to add the mapping.

---

### 9. Create Uploads Directory

```bash
cd /home/Swowroop/Community_event
mkdir -p static/uploads
```

---

### 10. Reload Application

Go to **Web** tab → Click **Reload**

---

### 11. Visit Your Site

Open: `https://Swowroop.pythonanywhere.com`

---

## Troubleshooting

**Check error logs:** Web tab → Click **Error log**

**Common fixes:**

- Missing dependencies → Run `pip install -r requirements.txt` again
- Database error → Run `flask create-db`
- Import error → Check WSGI file path is correct

---

## Updating Your Deployment

After pushing changes to GitHub:

```bash
cd ~/Community_event
git pull origin main
```

Then go to **Web** tab → **Reload**
