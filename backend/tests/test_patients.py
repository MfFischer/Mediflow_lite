"""
Tests for patient management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.models.user import User
from app.models.patient import Patient
from app.core.security import get_password_hash


@pytest.fixture
def auth_headers(client, db_session):
    """Create a test user and return authentication headers."""
    # Create test user
    user = User(
        username="testdoctor",
        hashed_password=get_password_hash("TestPassword123!"),
        role="doctor"
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testdoctor", "password": "TestPassword123!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_patient(db_session):
    """Create a sample patient for testing."""
    patient = Patient(
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 15),
        email="john.doe@example.com",
        phone_number="+1234567890"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


class TestPatientEndpoints:
    """Test suite for patient management endpoints."""
    
    def test_create_patient_success(self, client, auth_headers):
        """Test successful patient creation."""
        patient_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-05-20",
            "email": "jane.smith@example.com",
            "phone_number": "+1234567891"
        }
        
        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["email"] == "jane.smith@example.com"
        assert "id" in data
    
    def test_create_patient_duplicate_email(self, client, auth_headers, sample_patient):
        """Test that duplicate email is rejected."""
        patient_data = {
            "first_name": "Another",
            "last_name": "Person",
            "date_of_birth": "1990-01-01",
            "email": sample_patient.email,  # Duplicate email
            "phone_number": "+1234567892"
        }
        
        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_create_patient_invalid_email(self, client, auth_headers):
        """Test that invalid email is rejected."""
        patient_data = {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "email": "invalid-email",
            "phone_number": "+1234567890"
        }
        
        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_create_patient_future_dob(self, client, auth_headers):
        """Test that future date of birth is rejected."""
        patient_data = {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "2030-01-01",
            "email": "test@example.com",
            "phone_number": "+1234567890"
        }
        
        response = client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_list_patients(self, client, auth_headers, sample_patient):
        """Test listing patients with pagination."""
        response = client.get(
            "/api/v1/patients/?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "patients" in data
        assert len(data["patients"]) > 0
    
    def test_list_patients_with_search(self, client, auth_headers, sample_patient):
        """Test searching patients by name."""
        response = client.get(
            f"/api/v1/patients/?search={sample_patient.first_name}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert any(p["first_name"] == sample_patient.first_name for p in data["patients"])
    
    def test_get_patient_by_id(self, client, auth_headers, sample_patient):
        """Test getting a specific patient by ID."""
        response = client.get(
            f"/api/v1/patients/{sample_patient.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_patient.id
        assert data["first_name"] == sample_patient.first_name
    
    def test_get_patient_not_found(self, client, auth_headers):
        """Test getting a non-existent patient."""
        response = client.get(
            "/api/v1/patients/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_patient(self, client, auth_headers, sample_patient):
        """Test updating a patient."""
        update_data = {
            "first_name": "UpdatedName",
            "phone_number": "+9876543210"
        }
        
        response = client.put(
            f"/api/v1/patients/{sample_patient.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "UpdatedName"
        assert data["phone_number"] == "+9876543210"
        assert data["last_name"] == sample_patient.last_name  # Unchanged
    
    def test_delete_patient_forbidden(self, client, auth_headers, sample_patient):
        """Test that non-admin cannot delete patient."""
        response = client.delete(
            f"/api/v1/patients/{sample_patient.id}",
            headers=auth_headers
        )
        
        # Doctor role should not be able to delete
        assert response.status_code == 403
    
    def test_unauthorized_access(self, client, sample_patient):
        """Test that unauthenticated requests are rejected."""
        response = client.get("/api/v1/patients/")
        assert response.status_code == 401
        
        response = client.get(f"/api/v1/patients/{sample_patient.id}")
        assert response.status_code == 401
        
        response = client.post("/api/v1/patients/", json={})
        assert response.status_code == 401

