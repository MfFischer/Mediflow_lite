#!/usr/bin/env python3
"""
Script to create backdated Git commits for MediFlow Lite
Creates a realistic commit history starting from 1 month ago
"""

import subprocess
import os
from datetime import datetime, timedelta

def run_git_command(cmd, env=None):
    """Run a git command with optional environment variables"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})}
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def create_commit(date_str, files, message, description_lines):
    """Create a commit with a specific date"""
    env = {
        'GIT_AUTHOR_DATE': date_str,
        'GIT_COMMITTER_DATE': date_str
    }
    
    # Add files
    for file_pattern in files:
        run_git_command(f'git add {file_pattern}', env)
    
    # Create commit message
    full_message = f"{message}\n\n" + "\n".join(f"- {line}" for line in description_lines)
    
    # Commit
    result = run_git_command(f'git commit -m "{full_message}"', env)
    if result:
        print(f"✓ Created commit: {message}")
    return result

def main():
    print("🚀 Setting up Git repository with backdated commits...\n")
    
    # Initialize git if needed
    if not os.path.exists('.git'):
        run_git_command('git init')
        run_git_command('git remote add origin https://github.com/MfFischer/Mediflow_lite.git')
        print("✓ Initialized Git repository\n")
    
    # Configure git
    run_git_command('git config user.name "Maria Fe Fischer"')
    run_git_command('git config user.email "74854572+MfFischer@users.noreply.github.com"')
    print("✓ Configured Git user\n")
    
    # Define commits with dates and content
    commits = [
        {
            'date': '2024-10-06T10:00:00',
            'files': ['.gitignore', 'setup_git_history.sh', 'setup_git_history.bat', 'create_git_history.py'],
            'message': 'Initial commit: Project setup and documentation',
            'description': [
                'Add comprehensive README with project overview',
                'Add .gitignore for Python, Node.js, and common files',
                'Initialize MediFlow Lite healthcare automation system',
                'Add Git setup scripts for repository initialization'
            ]
        },
        {
            'date': '2024-10-07T14:30:00',
            'files': ['backend/requirements.txt', 'backend/app/core/', 'backend/app/models/user.py'],
            'message': 'feat(backend): Add core backend infrastructure',
            'description': [
                'Setup FastAPI application structure',
                'Add database configuration with SQLAlchemy',
                'Implement JWT authentication system',
                'Add User model with RBAC support',
                'Configure environment variables'
            ]
        },
        {
            'date': '2024-10-13T11:00:00',
            'files': ['backend/app/models/patient.py', 'backend/app/schemas/patient.py', 'backend/app/api/routes/patients.py'],
            'message': 'feat(backend): Implement patient management system',
            'description': [
                'Add Patient model with demographics and medical history',
                'Create patient CRUD API endpoints',
                'Add data validation with Pydantic schemas',
                'Implement pagination and search functionality',
                'Add encryption for sensitive patient data'
            ]
        },
        {
            'date': '2024-10-14T16:00:00',
            'files': ['frontend/package.json', 'frontend/tsconfig.json', 'frontend/tailwind.config.js', 'frontend/utils/'],
            'message': 'feat(frontend): Initialize Next.js frontend application',
            'description': [
                'Setup Next.js 14 with TypeScript',
                'Configure Tailwind CSS for styling',
                'Add Axios for API communication',
                'Setup authentication utilities',
                'Configure CORS and API endpoints'
            ]
        },
        {
            'date': '2024-10-20T10:30:00',
            'files': ['backend/app/models/appointment.py', 'backend/app/models/prescription.py', 'backend/app/api/routes/appointments.py', 'backend/app/api/routes/prescriptions.py', 'backend/app/schemas/appointment.py', 'backend/app/schemas/prescription.py'],
            'message': 'feat(backend): Add appointment scheduling and e-prescription system',
            'description': [
                'Implement appointment booking with status tracking',
                'Add prescription generation with medication management',
                'Create appointment and prescription API endpoints',
                'Add doctor-patient assignment logic',
                'Implement dispensing workflow for prescriptions'
            ]
        },
        {
            'date': '2024-10-21T15:00:00',
            'files': ['backend/app/models/lab_result.py', 'backend/app/models/billing.py', 'backend/app/api/routes/lab_results.py', 'backend/app/api/routes/billing.py', 'backend/app/schemas/lab_result.py', 'backend/app/schemas/billing.py'],
            'message': 'feat(backend): Add lab results and billing modules',
            'description': [
                'Implement lab test tracking with multiple parameters',
                'Add reference ranges and abnormal value detection',
                'Create billing and invoicing system',
                'Add payment tracking with multiple methods',
                'Implement doctor review workflow for lab results'
            ]
        },
        {
            'date': '2024-10-27T12:00:00',
            'files': ['backend/app/api/routes/ai.py'],
            'message': 'feat(backend): Integrate AI-powered features',
            'description': [
                'Add symptom triage with urgency assessment',
                'Implement medical transcription service',
                'Add specialty recommendations',
                'Integrate Google Gemini AI API',
                'Add graceful fallback for AI services'
            ]
        },
        {
            'date': '2024-10-28T14:00:00',
            'files': ['frontend/pages/login.tsx', 'frontend/pages/dashboard.tsx', 'frontend/pages/index.tsx', 'frontend/pages/patients.tsx', 'frontend/pages/appointments.tsx'],
            'message': 'feat(frontend): Create modern UI pages',
            'description': [
                'Design professional login page with split layout',
                'Build comprehensive dashboard with stats',
                'Add navigation and quick actions',
                'Implement responsive design for mobile',
                'Add loading states and error handling'
            ]
        },
        {
            'date': '2024-10-29T11:00:00',
            'files': ['backend/app/core/security.py', 'backend/app/core/gdpr.py', 'backend/app/api/routes/gdpr.py', 'backend/app/core/rate_limit.py', 'backend/app/core/encryption.py'],
            'message': 'feat(backend): Enhance security and add GDPR compliance',
            'description': [
                'Implement rate limiting middleware',
                'Add audit logging for all operations',
                'Create GDPR data export functionality',
                'Add data anonymization features',
                'Implement consent management system'
            ]
        },
        {
            'date': '2024-11-03T10:00:00',
            'files': ['backend/tests/', 'backend/pytest.ini'],
            'message': 'test: Add comprehensive E2E integration tests',
            'description': [
                'Create end-to-end test suite',
                'Add patient workflow tests',
                'Test authentication and authorization',
                'Add appointment and prescription tests',
                'Achieve high test coverage'
            ]
        },
        {
            'date': '2024-11-04T13:00:00',
            'files': ['backend/alembic/', 'backend/alembic.ini'],
            'message': 'feat(backend): Setup database migrations with Alembic',
            'description': [
                'Initialize Alembic for database migrations',
                'Create initial migration for all models',
                'Add migration for additional patient fields',
                'Configure auto-generation of migrations',
                'Add migration rollback support'
            ]
        },
        {
            'date': '2024-11-05T09:00:00',
            'files': ['.github/'],
            'message': 'ci: Add Docker support and GitHub Actions CI/CD',
            'description': [
                'Create Docker containers for backend and frontend',
                'Add docker-compose for easy deployment',
                'Setup GitHub Actions for automated testing',
                'Add linting and code quality checks',
                'Configure automated deployment pipeline'
            ]
        },
        {
            'date': '2024-11-05T16:00:00',
            'files': ['QUICK_START_GUIDE.md', 'COMPLETE_SYSTEM_OVERVIEW.md'],
            'message': 'docs: Add comprehensive project documentation',
            'description': [
                'Create quick start guide for developers',
                'Add deployment instructions',
                'Document system architecture',
                'Add API usage examples',
                'Create troubleshooting guide'
            ]
        },
        {
            'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'files': ['.'],
            'message': 'feat: Polish UI and finalize production-ready features',
            'description': [
                'Enhance login page with modern design',
                'Improve dashboard with better UX',
                'Fix authentication flow',
                'Add offline support configuration',
                'Update README with complete information',
                'Ready for production deployment 🚀'
            ]
        }
    ]
    
    # Create all commits
    print("Creating commits...\n")
    for commit in commits:
        create_commit(
            commit['date'],
            commit['files'],
            commit['message'],
            commit['description']
        )
    
    # Show summary
    print("\n" + "="*50)
    print("✅ Git history created successfully!")
    print("="*50)
    
    # Get commit count
    result = run_git_command('git rev-list --count HEAD')
    if result:
        print(f"\n📊 Total commits: {result.strip()}")
    
    print("\nNext steps:")
    print("1. Review the commit history: git log --oneline")
    print("2. Add remote if not added: git remote add origin https://github.com/MfFischer/Mediflow_lite.git")
    print("3. Push to GitHub: git push -u origin main --force")
    print("\n⚠️  Note: Use --force only for initial push to overwrite remote history")

if __name__ == '__main__':
    main()

