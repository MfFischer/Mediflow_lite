"""
AI Chat API endpoints
Provides intelligent database querying through natural language
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

from ...core.database import get_db
from ...core.rbac import require_role
from ...models.user import User
from ...models.enums import UserRole
from ...services.ai_assistant import AIAssistant, DatabaseQueryTools


router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's question")
    use_local: bool = Field(default=False, description="Force use of local LLM (offline mode)")
    clear_history: bool = Field(default=False, description="Clear conversation history before this message")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    tool_calls: List[Dict[str, Any]] = []
    model_used: str
    is_database_query: bool = True
    timestamp: str


class ToolListResponse(BaseModel):
    """Available tools response"""
    tools: List[Dict[str, Any]]
    total: int


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.NURSE,
        UserRole.RECEPTIONIST,
        UserRole.ACCOUNTANT
    ]))
):
    """
    Chat with AI assistant about database queries
    
    The AI can answer questions about:
    - Patients (count, search, details)
    - Doctors (schedules, appointments)
    - Appointments (statistics, status)
    - Financial data (revenue, expenses, profit)
    
    The AI will NOT answer general medical questions.
    """
    try:
        assistant = AIAssistant(db)
        
        if request.clear_history:
            assistant.clear_history()
        
        response = await assistant.chat(
            user_message=request.message,
            use_local=request.use_local
        )
        
        from datetime import datetime
        response["timestamp"] = datetime.now().isoformat()
        
        return ChatResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI assistant error: {str(e)}"
        )


@router.get("/tools", response_model=ToolListResponse)
async def get_available_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.NURSE,
        UserRole.RECEPTIONIST,
        UserRole.ACCOUNTANT
    ]))
):
    """
    Get list of available database query tools
    
    Returns all tools that the AI can use to query the database
    """
    tools_instance = DatabaseQueryTools(db)
    tools = tools_instance.get_available_tools()
    
    return ToolListResponse(
        tools=tools,
        total=len(tools)
    )


@router.post("/query/patients/count")
async def query_patient_count(
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.RECEPTIONIST
    ]))
):
    """Direct API to get patient count"""
    tools = DatabaseQueryTools(db)
    return tools.get_patient_count(filters)


@router.post("/query/patients/search")
async def query_search_patients(
    search_term: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.NURSE,
        UserRole.RECEPTIONIST
    ]))
):
    """Direct API to search patients"""
    tools = DatabaseQueryTools(db)
    return tools.search_patients(search_term, limit)


@router.get("/query/patients/{patient_id}")
async def query_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.NURSE,
        UserRole.RECEPTIONIST
    ]))
):
    """Direct API to get patient details"""
    tools = DatabaseQueryTools(db)
    return tools.get_patient_details(patient_id=patient_id)


@router.post("/query/doctors/schedule")
async def query_doctor_schedule(
    doctor_name: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.RECEPTIONIST
    ]))
):
    """Direct API to get doctor's schedule"""
    tools = DatabaseQueryTools(db)
    return tools.get_doctor_schedule(doctor_name, date_from, date_to)


@router.post("/query/financial/summary")
async def query_financial_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.ACCOUNTANT
    ]))
):
    """Direct API to get financial summary"""
    tools = DatabaseQueryTools(db)
    return tools.get_financial_summary(date_from, date_to)


@router.post("/query/appointments/stats")
async def query_appointment_stats(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.RECEPTIONIST
    ]))
):
    """Direct API to get appointment statistics"""
    tools = DatabaseQueryTools(db)
    return tools.get_appointment_stats(date_from, date_to)


@router.get("/status")
async def get_ai_status(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Get AI assistant status and configuration
    
    Shows which AI backends are available (OpenAI, local LLM)
    """
    from ...core.config import settings
    import os
    
    openai_available = bool(settings.openai_api_key)
    local_model_exists = os.path.exists(settings.local_llm_model_path) if settings.local_llm_enabled else False
    
    return {
        "openai": {
            "enabled": openai_available,
            "model": settings.openai_model if openai_available else None
        },
        "local_llm": {
            "enabled": settings.local_llm_enabled,
            "model_path": settings.local_llm_model_path,
            "model_exists": local_model_exists
        },
        "fallback_enabled": settings.ai_fallback_to_local,
        "status": "online" if (openai_available or local_model_exists) else "offline"
    }


@router.post("/clear-history")
async def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN,
        UserRole.DOCTOR,
        UserRole.NURSE,
        UserRole.RECEPTIONIST,
        UserRole.ACCOUNTANT
    ]))
):
    """Clear conversation history"""
    # In production, you'd want to store history per user
    # For now, this is a placeholder
    return {
        "message": "Chat history cleared",
        "user_id": current_user.id
    }

