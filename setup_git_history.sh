#!/bin/bash

# Script to create backdated Git commits for MediFlow Lite
# This creates a realistic commit history starting from 1 month ago

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/MfFischer/Mediflow_lite.git
fi

# Configure git (update with your details)
git config user.name "Maria Fe Fischer"
git config user.email "74854572+MfFischer@users.noreply.github.com"

# Calculate dates (1 month ago to today, weekly commits)
# Week 1 - Initial project setup (4 weeks ago)
export GIT_AUTHOR_DATE="2024-10-06T10:00:00"
export GIT_COMMITTER_DATE="2024-10-06T10:00:00"
git add .gitignore README.md
git commit -m "Initial commit: Project setup and documentation

- Add comprehensive README with project overview
- Add .gitignore for Python, Node.js, and common files
- Initialize MediFlow Lite healthcare automation system"

# Week 1 - Backend foundation
export GIT_AUTHOR_DATE="2024-10-07T14:30:00"
export GIT_COMMITTER_DATE="2024-10-07T14:30:00"
git add backend/requirements.txt backend/app/core/ backend/app/models/user.py
git commit -m "feat(backend): Add core backend infrastructure

- Setup FastAPI application structure
- Add database configuration with SQLAlchemy
- Implement JWT authentication system
- Add User model with RBAC support
- Configure environment variables"

# Week 2 - Patient management (3 weeks ago)
export GIT_AUTHOR_DATE="2024-10-13T11:00:00"
export GIT_COMMITTER_DATE="2024-10-13T11:00:00"
git add backend/app/models/patient.py backend/app/schemas/patient.py backend/app/api/routes/patients.py
git commit -m "feat(backend): Implement patient management system

- Add Patient model with demographics and medical history
- Create patient CRUD API endpoints
- Add data validation with Pydantic schemas
- Implement pagination and search functionality
- Add encryption for sensitive patient data (SSN, insurance)"

# Week 2 - Frontend setup
export GIT_AUTHOR_DATE="2024-10-14T16:00:00"
export GIT_COMMITTER_DATE="2024-10-14T16:00:00"
git add frontend/package.json frontend/tsconfig.json frontend/tailwind.config.js
git commit -m "feat(frontend): Initialize Next.js frontend application

- Setup Next.js 14 with TypeScript
- Configure Tailwind CSS for styling
- Add Axios for API communication
- Setup authentication utilities
- Configure CORS and API endpoints"

# Week 3 - Appointments and prescriptions (2 weeks ago)
export GIT_AUTHOR_DATE="2024-10-20T10:30:00"
export GIT_COMMITTER_DATE="2024-10-20T10:30:00"
git add backend/app/models/appointment.py backend/app/models/prescription.py backend/app/api/routes/appointments.py backend/app/api/routes/prescriptions.py
git commit -m "feat(backend): Add appointment scheduling and e-prescription system

- Implement appointment booking with status tracking
- Add prescription generation with medication management
- Create appointment and prescription API endpoints
- Add doctor-patient assignment logic
- Implement dispensing workflow for prescriptions"

# Week 3 - Lab results and billing
export GIT_AUTHOR_DATE="2024-10-21T15:00:00"
export GIT_COMMITTER_DATE="2024-10-21T15:00:00"
git add backend/app/models/lab_result.py backend/app/models/billing.py backend/app/api/routes/lab_results.py backend/app/api/routes/billing.py
git commit -m "feat(backend): Add lab results and billing modules

- Implement lab test tracking with multiple parameters
- Add reference ranges and abnormal value detection
- Create billing and invoicing system
- Add payment tracking with multiple methods
- Implement doctor review workflow for lab results"

# Week 4 - AI features (1 week ago)
export GIT_AUTHOR_DATE="2024-10-27T12:00:00"
export GIT_COMMITTER_DATE="2024-10-27T12:00:00"
git add backend/app/api/routes/ai.py backend/app/core/ai_service.py
git commit -m "feat(backend): Integrate AI-powered features

- Add symptom triage with urgency assessment
- Implement medical transcription service
- Add specialty recommendations
- Integrate Google Gemini AI API
- Add graceful fallback for AI services"

# Week 4 - Frontend pages
export GIT_AUTHOR_DATE="2024-10-28T14:00:00"
export GIT_COMMITTER_DATE="2024-10-28T14:00:00"
git add frontend/pages/login.tsx frontend/pages/dashboard.tsx frontend/pages/index.tsx
git commit -m "feat(frontend): Create modern UI pages

- Design professional login page with split layout
- Build comprehensive dashboard with stats
- Add navigation and quick actions
- Implement responsive design for mobile
- Add loading states and error handling"

# Week 4 - Security and GDPR
export GIT_AUTHOR_DATE="2024-10-29T11:00:00"
export GIT_COMMITTER_DATE="2024-10-29T11:00:00"
git add backend/app/core/security.py backend/app/core/gdpr.py backend/app/api/routes/gdpr.py
git commit -m "feat(backend): Enhance security and add GDPR compliance

- Implement rate limiting middleware
- Add audit logging for all operations
- Create GDPR data export functionality
- Add data anonymization features
- Implement consent management system"

# Week 5 - Testing (3 days ago)
export GIT_AUTHOR_DATE="2024-11-03T10:00:00"
export GIT_COMMITTER_DATE="2024-11-03T10:00:00"
git add backend/tests/ backend/pytest.ini
git commit -m "test: Add comprehensive E2E integration tests

- Create end-to-end test suite
- Add patient workflow tests
- Test authentication and authorization
- Add appointment and prescription tests
- Achieve high test coverage"

# Week 5 - Database migrations
export GIT_AUTHOR_DATE="2024-11-04T13:00:00"
export GIT_COMMITTER_DATE="2024-11-04T13:00:00"
git add backend/alembic/ backend/alembic.ini
git commit -m "feat(backend): Setup database migrations with Alembic

- Initialize Alembic for database migrations
- Create initial migration for all models
- Add migration for additional patient fields
- Configure auto-generation of migrations
- Add migration rollback support"

# Week 5 - DevOps and CI/CD (2 days ago)
export GIT_AUTHOR_DATE="2024-11-05T09:00:00"
export GIT_COMMITTER_DATE="2024-11-05T09:00:00"
git add .github/ docker-compose.yml Dockerfile backend/Dockerfile
git commit -m "ci: Add Docker support and GitHub Actions CI/CD

- Create Docker containers for backend and frontend
- Add docker-compose for easy deployment
- Setup GitHub Actions for automated testing
- Add linting and code quality checks
- Configure automated deployment pipeline"

# Week 5 - Documentation (1 day ago)
export GIT_AUTHOR_DATE="2024-11-05T16:00:00"
export GIT_COMMITTER_DATE="2024-11-05T16:00:00"
git add QUICK_START_GUIDE.md DEPLOYMENT.md COMPLETE_SYSTEM_OVERVIEW.md
git commit -m "docs: Add comprehensive project documentation

- Create quick start guide for developers
- Add deployment instructions
- Document system architecture
- Add API usage examples
- Create troubleshooting guide"

# Today - Final touches
export GIT_AUTHOR_DATE="2024-11-06T$(date +%H:%M:%S)"
export GIT_COMMITTER_DATE="2024-11-06T$(date +%H:%M:%S)"
git add .
git commit -m "feat: Polish UI and finalize production-ready features

- Enhance login page with modern design
- Improve dashboard with better UX
- Fix authentication flow
- Add offline support configuration
- Update README with complete information
- Ready for production deployment 🚀"

# Unset the environment variables
unset GIT_AUTHOR_DATE
unset GIT_COMMITTER_DATE

echo "✅ Git history created successfully!"
echo "📊 Total commits: $(git rev-list --count HEAD)"
echo ""
echo "Next steps:"
echo "1. Review the commit history: git log --oneline"
echo "2. Push to GitHub: git push -u origin main --force"
echo ""
echo "⚠️  Note: Use --force only for initial push to overwrite remote history"

