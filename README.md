# Enterprise College Management System (CMS)

Welcome to the Enterprise College Management System! This application is a fully-featured, role-based management dashboard for educational institutions, built with modern web technologies and robust backend architecture.

## 🚀 How to Run the Project

### Prerequisites
- Python 3.9 or higher installed on your system.

### Step 1: Clone or Navigate to the Project Directory
Ensure you are in the root directory of the project (where `run.py` is located).
```bash
cd CMS
```

### Step 2: Create a Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.
```bash
# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
```bash
# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 4: Install Dependencies
Install all required Python packages from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
Start the FastAPI server using the provided `run.py` script. The application uses SQLite, so the database and demo data will be automatically generated upon the first startup.
```bash
python run.py
```

### Step 6: Access the Dashboard
Open your web browser and go to:
- **Web Interface:** [http://localhost:8000](http://localhost:8000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 🔑 Demo Credentials
The system automatically seeds demo users during the first run. All demo users share the same default password: **`admin123`**

- **Admin:** `admin@cms.edu`
- **Teacher:** `teacher@cms.edu`
- **Student:** `student1@cms.edu`
- **HOD:** `hod_cs@cms.edu`
- **Accountant:** `accountant@cms.edu`
- **Librarian:** `librarian@cms.edu`

---

## 🛠️ Troubleshooting
- **Database Issues:** If you encounter database errors or want to start fresh, simply delete the `cms.db` file in the root directory. Running `python run.py` again will recreate the database and re-seed the demo data.
- **Port Conflict:** If port 8000 is already in use, you can modify the `uvicorn.run()` port in `run.py`.
