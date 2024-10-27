from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.config import settings
from app.models.user import User
from app.models.audit_event import AuditEvent

# Try to import Gemini, but don't fail if not available
try:
    import google.generativeai as genai
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
    else:
        model = None
except ImportError:
    model = None


router = APIRouter()


class TriageRequest(BaseModel):
    """Request for AI-powered triage."""
    symptoms: str = Field(..., min_length=10, max_length=2000, description="Patient symptoms")
    age: Optional[int] = Field(None, ge=0, le=150, description="Patient age")
    medical_history: Optional[str] = Field(None, max_length=1000, description="Relevant medical history")


class TriageResponse(BaseModel):
    """Response from AI triage."""
    urgency_level: str  # "emergency", "urgent", "routine", "non-urgent"
    suggested_specialty: str
    recommendations: List[str]
    disclaimer: str


class TranscriptionRequest(BaseModel):
    """Request for medical transcription."""
    audio_text: str = Field(..., min_length=10, max_length=5000, description="Transcribed audio text")
    context: Optional[str] = Field(None, description="Context (e.g., 'consultation', 'diagnosis')")


class TranscriptionResponse(BaseModel):
    """Response from medical transcription."""
    structured_notes: str
    key_points: List[str]
    suggested_diagnosis: Optional[str]
    suggested_tests: List[str]


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Helper to log audit events."""
    audit_event = AuditEvent(action=action, user_id=user_id, details=details)
    db.add(audit_event)
    db.commit()


@router.post("/triage", response_model=TriageResponse)
async def ai_triage(
    request: TriageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """
    AI-powered symptom triage.

    Analyzes patient symptoms and provides urgency assessment and recommendations.
    """
    if not model:
        # Return mock response if AI not configured
        return TriageResponse(
            urgency_level="routine",
            suggested_specialty="General Practice",
            recommendations=[
                "Schedule a consultation with a healthcare provider",
                "Monitor symptoms and note any changes",
                "Maintain a healthy lifestyle"
            ],
            disclaimer="AI service not configured. This is a default response. Please consult a healthcare provider."
        )

    try:
        # Build prompt
        prompt = f"""You are a medical triage assistant. Analyze the following patient information and provide a triage assessment.

Symptoms: {request.symptoms}
Age: {request.age if request.age else 'Not provided'}
Medical History: {request.medical_history if request.medical_history else 'Not provided'}

Provide your assessment in the following format:
1. Urgency Level: (emergency/urgent/routine/non-urgent)
2. Suggested Specialty: (e.g., cardiology, orthopedics, general practice)
3. Recommendations: (list 3-5 specific recommendations)

Remember: This is for triage purposes only and not a medical diagnosis."""

        response = model.generate_content(prompt)
        result_text = response.text

        # Parse response
        lines = result_text.split('\n')
        urgency_level = "routine"
        suggested_specialty = "General Practice"
        recommendations = []

        for line in lines:
            if "urgency" in line.lower():
                if "emergency" in line.lower():
                    urgency_level = "emergency"
                elif "urgent" in line.lower():
                    urgency_level = "urgent"
                elif "non-urgent" in line.lower():
                    urgency_level = "non-urgent"
            elif "specialty" in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    suggested_specialty = parts[1].strip()
            elif line.strip().startswith(('-', '•', '*')) or (line.strip() and line.strip()[0].isdigit()):
                recommendations.append(line.strip().lstrip('-•*0123456789. '))

        # Log audit event
        log_audit_event(
            db,
            "AI_TRIAGE",
            current_user.id,
            f"AI triage performed - Urgency: {urgency_level}"
        )

        return TriageResponse(
            urgency_level=urgency_level,
            suggested_specialty=suggested_specialty,
            recommendations=recommendations[:5] if recommendations else ["Consult with a healthcare provider"],
            disclaimer="This is an AI-generated assessment and should not replace professional medical advice."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )



@router.post("/transcribe", response_model=TranscriptionResponse)
async def ai_transcribe(
    request: TranscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """
    AI-powered medical transcription.

    Converts consultation notes into structured medical documentation.
    """
    if not model:
        return TranscriptionResponse(
            structured_notes="AI service not configured. Please manually structure your notes.",
            key_points=["AI service unavailable"],
            suggested_diagnosis=None,
            suggested_tests=[]
        )

    try:
        prompt = f"""You are a medical transcription assistant. Convert the following consultation notes into structured medical documentation.

Context: {request.context if request.context else 'General consultation'}
Notes: {request.audio_text}

Provide:
1. Structured Notes: A well-organized summary
2. Key Points: 3-5 most important points
3. Suggested Diagnosis: If applicable (or "Further evaluation needed")
4. Suggested Tests: Any recommended diagnostic tests

Format your response clearly with these sections."""

        response = model.generate_content(prompt)
        result_text = response.text

        # Parse response (simplified)
        structured_notes = result_text
        key_points = ["Consultation documented", "Review recommended"]
        suggested_diagnosis = "Further evaluation needed"
        suggested_tests = []

        # Log audit event
        log_audit_event(
            db,
            "AI_TRANSCRIPTION",
            current_user.id,
            "AI transcription performed"
        )

        return TranscriptionResponse(
            structured_notes=structured_notes,
            key_points=key_points,
            suggested_diagnosis=suggested_diagnosis,
            suggested_tests=suggested_tests
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """Check if AI service is available."""
    return {
        "ai_service_available": model is not None,
        "service": "Google Gemini" if model else "Not configured",
        "message": "AI service is ready" if model else "Set GEMINI_API_KEY to enable AI features"
    }
