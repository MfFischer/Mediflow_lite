"""Quick script to create demo users."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if users exist
    from sqlalchemy import text
    result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    
    if result > 0:
        print(f"✅ Found {result} existing users")
        users = db.execute(text("SELECT username, role FROM users")).fetchall()
        for username, role in users:
            print(f"   - {username} ({role})")
    else:
        print("Creating demo users...")
        
        # Insert users directly
        admin_hash = get_password_hash("admin123")
        doctor_hash = get_password_hash("doctor123")
        receptionist_hash = get_password_hash("receptionist123")
        
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, role)
            VALUES
                ('admin', 'admin@mediflow.local', :admin_hash, 'admin'),
                ('doctor', 'doctor@mediflow.local', :doctor_hash, 'doctor'),
                ('receptionist', 'receptionist@mediflow.local', :receptionist_hash, 'receptionist')
        """), {
            'admin_hash': admin_hash,
            'doctor_hash': doctor_hash,
            'receptionist_hash': receptionist_hash
        })
        db.commit()
        
        print("✅ Created 3 demo users:")
        print("   - admin / admin123 (admin)")
        print("   - doctor / doctor123 (doctor)")
        print("   - receptionist / receptionist123 (receptionist)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()

