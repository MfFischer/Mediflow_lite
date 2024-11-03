"""
End-to-end integration tests for MediFlow Lite.

Tests complete workflows across all modules.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.core.database import Base, get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_e2e.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def admin_token(client):
    """Create admin user and get token."""
    from app.models.user import User
    from app.core.security import get_password_hash

    # Create admin user directly in database
    db = TestingSessionLocal()
    admin_user = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=get_password_hash("AdminPass123!"),
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.close()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "AdminPass123!"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def doctor_token(client):
    """Create doctor user and get token."""
    from app.models.user import User
    from app.core.security import get_password_hash

    # Create doctor user directly in database
    db = TestingSessionLocal()
    doctor_user = User(
        username="doctor_test",
        email="doctor@test.com",
        hashed_password=get_password_hash("DoctorPass123!"),
        role="doctor"
    )
    db.add(doctor_user)
    db.commit()
    db.close()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "doctor_test",
            "password": "DoctorPass123!"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_complete_patient_workflow(client, admin_token):
    """Test complete patient management workflow."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create patient
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "phone_number": "+1234567890",
        "date_of_birth": "1980-01-01",
        "gender": "male",
        "address": "123 Test St"
    }
    response = client.post("/api/v1/patients/", json=patient_data, headers=headers)
    assert response.status_code == 201, f"Failed to create patient: {response.json()}"
    patient = response.json()
    patient_id = patient["id"]

    # 2. Get patient
    response = client.get(f"/api/v1/patients/{patient_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "john.doe@test.com"

    # 3. Update patient
    response = client.put(
        f"/api/v1/patients/{patient_id}",
        json={"phone_number": "+9876543210"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["phone_number"] == "+9876543210"

    # 4. List patients
    response = client.get("/api/v1/patients/", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1

    return patient_id


def test_appointment_workflow(client, admin_token, doctor_token):
    """Test complete appointment scheduling workflow."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Create patient first
    patient_id = test_complete_patient_workflow(client, admin_token)
    
    # Get doctor ID
    response = client.get("/api/v1/auth/me", headers=doctor_headers)
    doctor_id = response.json()["id"]
    
    # 1. Check availability
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/appointments/availability",
        json={
            "doctor_id": doctor_id,
            "date": tomorrow,
            "duration_minutes": 30
        },
        headers=admin_headers
    )
    assert response.status_code == 200
    
    # 2. Create appointment
    appointment_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": tomorrow,
        "duration_minutes": 30,
        "appointment_type": "consultation",
        "notes": "Initial consultation"
    }
    response = client.post("/api/v1/appointments", json=appointment_data, headers=admin_headers)
    assert response.status_code == 201
    appointment = response.json()
    appointment_id = appointment["id"]
    
    # 3. Update appointment status
    response = client.put(
        f"/api/v1/appointments/{appointment_id}",
        json={"status": "confirmed"},
        headers=doctor_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    
    return appointment_id, patient_id, doctor_id


def test_prescription_workflow(client, doctor_token):
    """Test complete e-prescription workflow."""
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Get appointment data
    appointment_id, patient_id, doctor_id = test_appointment_workflow(client, headers, doctor_token)
    
    # 1. Create prescription
    prescription_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": appointment_id,
        "diagnosis": "Common cold with mild fever",
        "notes": "Rest and hydration recommended",
        "medications": [
            {
                "medication_name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Every 6 hours",
                "duration": "3 days",
                "instructions": "Take with food"
            },
            {
                "medication_name": "Vitamin C",
                "dosage": "1000mg",
                "frequency": "Once daily",
                "duration": "7 days",
                "instructions": "Take in the morning"
            }
        ]
    }
    response = client.post("/api/v1/prescriptions", json=prescription_data, headers=headers)
    assert response.status_code == 201
    prescription = response.json()
    prescription_id = prescription["id"]
    assert len(prescription["medications"]) == 2
    
    # 2. Get prescription
    response = client.get(f"/api/v1/prescriptions/{prescription_id}", headers=headers)
    assert response.status_code == 200
    
    # 3. Dispense prescription
    response = client.post(f"/api/v1/prescriptions/{prescription_id}/dispense", headers=headers)
    assert response.status_code == 200
    assert response.json()["dispensed"] is True
    
    return prescription_id


def test_lab_results_workflow(client, doctor_token):
    """Test complete lab results workflow."""
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Get appointment data
    appointment_id, patient_id, doctor_id = test_appointment_workflow(client, headers, doctor_token)
    
    # 1. Create lab result
    lab_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": appointment_id,
        "test_name": "Complete Blood Count (CBC)",
        "test_category": "Hematology",
        "test_date": datetime.utcnow().isoformat(),
        "notes": "Routine checkup",
        "test_values": [
            {
                "parameter_name": "Hemoglobin",
                "value": "14.5",
                "unit": "g/dL",
                "reference_range": "13.5-17.5",
                "is_abnormal": "normal"
            },
            {
                "parameter_name": "WBC Count",
                "value": "8.5",
                "unit": "10^3/μL",
                "reference_range": "4.5-11.0",
                "is_abnormal": "normal"
            }
        ]
    }
    response = client.post("/api/v1/lab-results", json=lab_data, headers=headers)
    assert response.status_code == 201
    lab_result = response.json()
    lab_result_id = lab_result["id"]
    assert len(lab_result["test_values"]) == 2
    
    # 2. Update lab result
    response = client.put(
        f"/api/v1/lab-results/{lab_result_id}",
        json={"status": "completed", "result_date": datetime.utcnow().isoformat()},
        headers=headers
    )
    assert response.status_code == 200
    
    # 3. Review lab result
    response = client.post(
        f"/api/v1/lab-results/{lab_result_id}/review",
        json={"comments": "All values within normal range"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "reviewed"
    
    return lab_result_id


def test_billing_workflow(client, admin_token):
    """Test complete billing workflow."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get appointment data
    appointment_id, patient_id, _ = test_appointment_workflow(client, headers, headers)
    
    # 1. Create invoice
    invoice_data = {
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "items": [
            {
                "description": "Consultation Fee",
                "quantity": 1,
                "unit_price": 100.00
            },
            {
                "description": "Lab Tests",
                "quantity": 2,
                "unit_price": 50.00
            }
        ],
        "tax_rate": 0.10,
        "discount_amount": 10.00
    }
    response = client.post("/api/v1/billing", json=invoice_data, headers=headers)
    assert response.status_code == 201
    invoice = response.json()
    invoice_id = invoice["id"]
    assert invoice["total_amount"] == 210.00  # (100 + 100) * 1.1 - 10
    
    # 2. Record payment
    response = client.post(
        f"/api/v1/billing/{invoice_id}/payment",
        json={"payment_method": "card"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    
    # 3. Get invoice statistics
    response = client.get("/api/v1/billing/summary/stats", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_invoices"] >= 1
    
    return invoice_id


def test_ai_features(client, doctor_token):
    """Test AI-powered features."""
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # 1. Test AI health check
    response = client.get("/api/v1/ai/health")
    assert response.status_code == 200
    
    # 2. Test symptom triage
    triage_data = {
        "symptoms": "Severe headache, fever, and stiff neck",
        "age": 35,
        "medical_history": "No significant medical history"
    }
    response = client.post("/api/v1/ai/triage", json=triage_data, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "urgency_level" in result
    assert "recommendations" in result
    
    # 3. Test medical transcription
    transcription_data = {
        "audio_text": "Patient presents with persistent cough for 2 weeks. No fever. Chest clear on auscultation.",
        "context": "consultation"
    }
    response = client.post("/api/v1/ai/transcribe", json=transcription_data, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "structured_notes" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

