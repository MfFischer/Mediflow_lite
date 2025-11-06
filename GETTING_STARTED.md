# Getting Started with MediFlow Lite

This guide will help you get MediFlow Lite up and running in minutes.

## 🚀 Quick Start (Recommended)

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repository)

### Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd mediflow
```

2. **Run the setup script**
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Create environment files with secure random keys
- Set up necessary directories
- Optionally start Docker containers

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. **Initialize with sample data**
```bash
docker-compose exec backend python scripts/init_db.py --with-sample-data
```

This creates sample users:
- **Admin**: `admin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Receptionist**: `receptionist` / `receptionist123`

---

## 🛠️ Manual Setup (For Development)

### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

Generate a secure secret key:
```bash
openssl rand -hex 32
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Initialize database with sample data**
```bash
python scripts/init_db.py --with-sample-data
```

6. **Start the development server**
```bash
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env if needed (default values work for local development)
```

3. **Start the development server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

---

## 📚 First Steps After Installation

### 1. Login to the System

Navigate to http://localhost:3000/login and use one of the sample accounts:
- Admin: `admin` / `admin123`
- Doctor: `doctor` / `doctor123`

### 2. Explore the API Documentation

Visit http://localhost:8000/docs to see:
- All available endpoints
- Request/response schemas
- Try out API calls directly

### 3. Create Your First Patient

**Via UI:**
1. Login as doctor or receptionist
2. Navigate to Patients page
3. Click "Add Patient"
4. Fill in the form and submit

**Via API:**
```bash
# Get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor","password":"doctor123"}'

# Create patient (use the access_token from above)
curl -X POST "http://localhost:8000/api/v1/patients/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890"
  }'
```

### 4. Test GDPR Compliance Features

**Export patient data:**
```bash
curl -X GET "http://localhost:8000/api/v1/gdpr/export/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Anonymize patient (admin only):**
```bash
curl -X POST "http://localhost:8000/api/v1/gdpr/anonymize/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🐳 Docker Commands

### Start all services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop all services
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Access database
```bash
docker-compose exec postgres psql -U mediflow -d mediflow
```

### Run migrations in Docker
```bash
docker-compose exec backend alembic upgrade head
```

---

## 🔧 Common Issues & Solutions

### Issue: Port already in use
**Solution:** Change ports in `docker-compose.yml` or stop conflicting services

### Issue: Database connection error
**Solution:** Ensure PostgreSQL is running and credentials are correct in `.env`

### Issue: Frontend can't connect to backend
**Solution:** Check `NEXT_PUBLIC_API_URL` in `frontend/.env` matches backend URL

### Issue: Authentication fails
**Solution:** Ensure `SECRET_KEY` is set in `backend/.env` and is the same across restarts

### Issue: Migrations fail
**Solution:** 
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

---

## 📖 Next Steps

1. **Read the API Documentation**
   - Visit http://localhost:8000/docs
   - Understand available endpoints and schemas

2. **Explore the Codebase**
   - Backend: `backend/app/` - FastAPI application
   - Frontend: `frontend/` - Next.js application
   - Tests: `backend/tests/` - pytest test suite

3. **Customize for Your Needs**
   - Add custom fields to models
   - Create new endpoints
   - Customize UI components

4. **Deploy to Production**
   - See `README.md` for deployment instructions
   - Configure production environment variables
   - Set up SSL/TLS certificates
   - Configure backup strategy

---

## 🆘 Getting Help

- **Documentation**: Check `README.md` and `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: http://localhost:8000/docs
- **Issues**: Open an issue on GitHub
- **Code Examples**: Check test files in `backend/tests/`

---

## 🎯 What to Build Next

Now that you have a working system, consider adding:

1. **Appointment Management**
   - Scheduling system
   - Calendar view
   - Automated reminders

2. **Billing System**
   - Invoice generation
   - Payment tracking
   - Insurance integration

3. **E-Prescriptions**
   - PDF generation
   - Digital signatures
   - Pharmacy integration

4. **Offline Mode**
   - Service workers
   - IndexedDB storage
   - Background sync

5. **AI Features**
   - Symptom triage
   - Medical transcription
   - Appointment suggestions

---

**Happy coding! 🏥💻**

