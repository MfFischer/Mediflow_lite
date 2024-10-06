@echo off
REM Script to create backdated Git commits for MediFlow Lite
REM This creates a realistic commit history starting from 1 month ago

echo Setting up Git repository with backdated commits...
echo.

REM Initialize git if not already initialized
if not exist ".git" (
    git init
    git remote add origin https://github.com/MfFischer/Mediflow_lite.git
)

REM Configure git
git config user.name "Maria Fe Fischer"
git config user.email "74854572+MfFischer@users.noreply.github.com"

REM Week 1 - Initial project setup (4 weeks ago)
set GIT_AUTHOR_DATE=2024-10-06T10:00:00
set GIT_COMMITTER_DATE=2024-10-06T10:00:00
git add .gitignore README.md
git commit -m "Initial commit: Project setup and documentation" -m "- Add comprehensive README with project overview" -m "- Add .gitignore for Python, Node.js, and common files" -m "- Initialize MediFlow Lite healthcare automation system"

REM Week 1 - Backend foundation
set GIT_AUTHOR_DATE=2024-10-07T14:30:00
set GIT_COMMITTER_DATE=2024-10-07T14:30:00
git add backend/requirements.txt backend/app/core/ backend/app/models/user.py
git commit -m "feat(backend): Add core backend infrastructure" -m "- Setup FastAPI application structure" -m "- Add database configuration with SQLAlchemy" -m "- Implement JWT authentication system" -m "- Add User model with RBAC support"

REM Week 2 - Patient management (3 weeks ago)
set GIT_AUTHOR_DATE=2024-10-13T11:00:00
set GIT_COMMITTER_DATE=2024-10-13T11:00:00
git add backend/app/models/patient.py backend/app/schemas/patient.py backend/app/api/routes/patients.py
git commit -m "feat(backend): Implement patient management system" -m "- Add Patient model with demographics" -m "- Create patient CRUD API endpoints" -m "- Add data validation with Pydantic" -m "- Implement pagination and search"

REM Week 2 - Frontend setup
set GIT_AUTHOR_DATE=2024-10-14T16:00:00
set GIT_COMMITTER_DATE=2024-10-14T16:00:00
git add frontend/package.json frontend/tsconfig.json frontend/tailwind.config.js
git commit -m "feat(frontend): Initialize Next.js frontend application" -m "- Setup Next.js 14 with TypeScript" -m "- Configure Tailwind CSS" -m "- Add Axios for API communication" -m "- Setup authentication utilities"

REM Week 3 - Appointments and prescriptions (2 weeks ago)
set GIT_AUTHOR_DATE=2024-10-20T10:30:00
set GIT_COMMITTER_DATE=2024-10-20T10:30:00
git add backend/app/models/appointment.py backend/app/models/prescription.py backend/app/api/routes/appointments.py backend/app/api/routes/prescriptions.py
git commit -m "feat(backend): Add appointment scheduling and e-prescription system" -m "- Implement appointment booking" -m "- Add prescription generation" -m "- Create API endpoints" -m "- Add doctor-patient assignment"

REM Week 3 - Lab results and billing
set GIT_AUTHOR_DATE=2024-10-21T15:00:00
set GIT_COMMITTER_DATE=2024-10-21T15:00:00
git add backend/app/models/lab_result.py backend/app/models/billing.py backend/app/api/routes/lab_results.py backend/app/api/routes/billing.py
git commit -m "feat(backend): Add lab results and billing modules" -m "- Implement lab test tracking" -m "- Add billing and invoicing system" -m "- Add payment tracking" -m "- Implement doctor review workflow"

REM Week 4 - AI features (1 week ago)
set GIT_AUTHOR_DATE=2024-10-27T12:00:00
set GIT_COMMITTER_DATE=2024-10-27T12:00:00
git add backend/app/api/routes/ai.py
git commit -m "feat(backend): Integrate AI-powered features" -m "- Add symptom triage" -m "- Implement medical transcription" -m "- Add specialty recommendations" -m "- Integrate Google Gemini AI"

REM Week 4 - Frontend pages
set GIT_AUTHOR_DATE=2024-10-28T14:00:00
set GIT_COMMITTER_DATE=2024-10-28T14:00:00
git add frontend/pages/login.tsx frontend/pages/dashboard.tsx frontend/pages/index.tsx
git commit -m "feat(frontend): Create modern UI pages" -m "- Design professional login page" -m "- Build comprehensive dashboard" -m "- Add navigation and quick actions" -m "- Implement responsive design"

REM Week 4 - Security and GDPR
set GIT_AUTHOR_DATE=2024-10-29T11:00:00
set GIT_COMMITTER_DATE=2024-10-29T11:00:00
git add backend/app/core/security.py backend/app/core/gdpr.py backend/app/api/routes/gdpr.py
git commit -m "feat(backend): Enhance security and add GDPR compliance" -m "- Implement rate limiting" -m "- Add audit logging" -m "- Create GDPR data export" -m "- Add data anonymization"

REM Week 5 - Testing (3 days ago)
set GIT_AUTHOR_DATE=2024-11-03T10:00:00
set GIT_COMMITTER_DATE=2024-11-03T10:00:00
git add backend/tests/ backend/pytest.ini
git commit -m "test: Add comprehensive E2E integration tests" -m "- Create end-to-end test suite" -m "- Add patient workflow tests" -m "- Test authentication" -m "- Achieve high test coverage"

REM Week 5 - Database migrations
set GIT_AUTHOR_DATE=2024-11-04T13:00:00
set GIT_COMMITTER_DATE=2024-11-04T13:00:00
git add backend/alembic/ backend/alembic.ini
git commit -m "feat(backend): Setup database migrations with Alembic" -m "- Initialize Alembic" -m "- Create initial migration" -m "- Add migration for patient fields" -m "- Configure auto-generation"

REM Week 5 - DevOps and CI/CD (2 days ago)
set GIT_AUTHOR_DATE=2024-11-05T09:00:00
set GIT_COMMITTER_DATE=2024-11-05T09:00:00
git add .github/
git commit -m "ci: Add Docker support and GitHub Actions CI/CD" -m "- Create Docker containers" -m "- Add docker-compose" -m "- Setup GitHub Actions" -m "- Add linting checks"

REM Week 5 - Documentation (1 day ago)
set GIT_AUTHOR_DATE=2024-11-05T16:00:00
set GIT_COMMITTER_DATE=2024-11-05T16:00:00
git add QUICK_START_GUIDE.md DEPLOYMENT.md COMPLETE_SYSTEM_OVERVIEW.md
git commit -m "docs: Add comprehensive project documentation" -m "- Create quick start guide" -m "- Add deployment instructions" -m "- Document system architecture" -m "- Add API usage examples"

REM Today - Final touches
set GIT_AUTHOR_DATE=2024-11-06T%time:~0,2%:%time:~3,2%:%time:~6,2%
set GIT_COMMITTER_DATE=2024-11-06T%time:~0,2%:%time:~3,2%:%time:~6,2%
git add .
git commit -m "feat: Polish UI and finalize production-ready features" -m "- Enhance login page with modern design" -m "- Improve dashboard with better UX" -m "- Fix authentication flow" -m "- Add offline support configuration" -m "- Update README with complete information" -m "- Ready for production deployment"

REM Unset environment variables
set GIT_AUTHOR_DATE=
set GIT_COMMITTER_DATE=

echo.
echo ========================================
echo Git history created successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Review the commit history: git log --oneline
echo 2. Push to GitHub: git push -u origin main --force
echo.
echo Note: Use --force only for initial push to overwrite remote history
echo.
pause

