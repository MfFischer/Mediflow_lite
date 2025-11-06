"""
Database initialization script.
Creates tables and optionally seeds with sample data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import init_db, SessionLocal
from app.core.security import pwd_context
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample data for development."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_user = db.query(User).first()
        if existing_user:
            logger.info("Sample data already exists. Skipping...")
            return
        
        logger.info("Creating sample data...")
        
        # Create sample users
        admin_user = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            role="admin"
        )
        doctor_user = User(
            username="doctor",
            hashed_password=pwd_context.hash("doctor123"),
            role="doctor"
        )
        receptionist_user = User(
            username="receptionist",
            hashed_password=pwd_context.hash("receptionist123"),
            role="receptionist"
        )
        
        db.add_all([admin_user, doctor_user, receptionist_user])
        db.commit()
        
        logger.info("✅ Sample users created:")
        logger.info("   - admin / admin123")
        logger.info("   - doctor / doctor123")
        logger.info("   - receptionist / receptionist123")
        
        # Create sample patients
        from datetime import date
        
        patient1 = Patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 15),
            email="john.doe@example.com",
            phone_number="+1234567890"
        )
        patient2 = Patient(
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1985, 5, 20),
            email="jane.smith@example.com",
            phone_number="+1234567891"
        )
        
        db.add_all([patient1, patient2])
        db.commit()
        
        logger.info("✅ Sample patients created")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function."""
    logger.info("Initializing database...")
    
    # Create tables
    init_db()
    logger.info("✅ Database tables created")
    
    # Ask if user wants sample data
    if len(sys.argv) > 1 and sys.argv[1] == "--with-sample-data":
        create_sample_data()
    else:
        logger.info("ℹ️  Run with --with-sample-data to create sample users and patients")
    
    logger.info("🎉 Database initialization complete!")


if __name__ == "__main__":
    main()

