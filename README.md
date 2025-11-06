# MediFlow Lite 🏥

**A Production-Ready Healthcare Automation System for Philippine Hospitals**

MediFlow Lite is a comprehensive, commercial-grade healthcare management system designed specifically for Philippine healthcare facilities. Built with modern technologies and Philippine healthcare standards in mind.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🌟 Key Features

### 🇵🇭 Philippine Healthcare Integration
- **PhilHealth Integration** - Complete PhilHealth member information tracking
- **HMO Support** - Major HMO providers (Maxicare, Medicard, Intellicare, etc.)
- **Senior Citizen & PWD Discounts** - Automatic 20% discount calculation
- **DOH Compliance** - Ready for Department of Health requirements
- **Professional Invoicing** - Hospital-grade billing with insurance breakdown

### 📋 Core Modules
- **Patient Management** - Comprehensive patient records with insurance details
- **Appointment Scheduling** - Real-time appointment booking and management
- **Prescriptions** - Digital prescription generation with medication tracking
- **Lab Results** - Laboratory test management with multiple test values
- **Billing & Invoicing** - Professional invoices with insurance coverage calculation
- **Dashboard & Analytics** - Real-time insights and statistics

### 🔒 Security & Compliance
- **JWT Authentication** - Secure access and refresh token system
- **Role-Based Access Control** - Admin, Doctor, and Receptionist roles
- **Data Encryption** - Sensitive medical data encryption
- **Audit Logging** - Complete audit trail for all operations
- **GDPR Compliant** - Privacy-first design

### 💼 Commercial-Grade Features
- **PDF Generation** - Professional prescription and invoice PDFs
- **Real-time Updates** - Live data synchronization
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Modern UI/UX** - Gradient designs, animations, and intuitive interface
- **Toast Notifications** - User-friendly feedback system

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **npm or yarn**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/MfFischer/Mediflow_lite.git
cd Mediflow_lite
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Database Setup**
```bash
# Run migrations
python -m alembic upgrade head
```

4. **Frontend Setup**
```bash
cd ../frontend
npm install
```

5. **Start the Application**

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Default Login Credentials
- **Admin**: `admin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Receptionist**: `receptionist` / `receptionist123`

---

## 📚 Documentation

For detailed system architecture, features, and implementation details, see:
- [Complete System Overview](COMPLETE_SYSTEM_OVERVIEW.md)

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with Alembic migrations
- **SQLite/PostgreSQL** - Database (SQLite for dev, PostgreSQL for production)
- **JWT** - Authentication and authorization
- **ReportLab** - PDF generation
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework with Pages Router
- **React 18** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Recharts** - Data visualization

---

## 📊 Project Structure

```
Mediflow_lite/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── utils/        # Utility functions
│   ├── alembic/          # Database migrations
│   └── tests/            # Backend tests
├── frontend/
│   ├── components/       # React components
│   ├── pages/           # Next.js pages
│   ├── public/          # Static assets
│   └── styles/          # Global styles
└── docs/                # Documentation
```

---

## 🇵🇭 Philippine Healthcare Features

### PhilHealth Integration
- 12-digit PhilHealth number tracking
- Member types: Member, Dependent, Senior Citizen, PWD
- Coverage amount calculation
- Ready for PhilHealth CF2 form generation

### HMO Support
Supported HMO providers:
- Maxicare
- Medicard
- Intellicare
- Cocolife
- PhilCare
- Avega
- Carewell
- Other

### Professional Invoicing
- Itemized billing by category:
  - Professional Fees (with doctor name and PRC license)
  - Laboratory Tests
  - Medications
  - Room Charges
  - Procedures
  - Medical Supplies
- Insurance breakdown:
  - PhilHealth coverage
  - HMO coverage
  - Senior Citizen/PWD discount (20%)
  - Patient balance calculation

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

---

## 🚢 Deployment

### Production Deployment

1. **Environment Variables**
Create `.env` file in backend:
```env
DATABASE_URL=postgresql://user:password@localhost/mediflow
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

2. **Database Migration**
```bash
python -m alembic upgrade head
```

3. **Build Frontend**
```bash
cd frontend
npm run build
npm start
```

4. **Run Backend**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Maria Fe Fischer** - [@MfFischer](https://github.com/MfFischer)

---

## 🙏 Acknowledgments

- Built with ❤️ for Philippine healthcare facilities
- Designed to meet DOH and PhilHealth standards
- Inspired by the need for affordable, modern healthcare management systems

---

**MediFlow Lite** - Empowering Philippine Healthcare 🇵🇭🏥

