"""
AI Assistant for MediFlow Lite
Database-focused AI that answers questions about patients, appointments, doctors, financials, etc.
Supports both online (OpenAI) and offline (local Phi-3) modes
"""
import json
import os
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..core.config import settings
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.user import User
from ..models.billing import Invoice
from ..models.financial import Payment, Expense, DoctorPayout


class DatabaseQueryTools:
    """Tools for AI to query the database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_patient_count(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get total patient count with optional filters"""
        query = self.db.query(Patient)
        
        if filters:
            if filters.get('date_from'):
                query = query.filter(Patient.created_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(Patient.created_at <= filters['date_to'])
        
        total = query.count()
        return {
            "total_patients": total,
            "filters_applied": filters or {}
        }
    
    def search_patients(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search patients by name, email, or phone"""
        search_pattern = f"%{search_term}%"
        patients = self.db.query(Patient).filter(
            or_(
                Patient.first_name.ilike(search_pattern),
                Patient.last_name.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
                Patient.phone.ilike(search_pattern)
            )
        ).limit(limit).all()
        
        return [{
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "email": p.email,
            "phone": p.phone,
            "date_of_birth": str(p.date_of_birth) if p.date_of_birth else None,
            "blood_type": p.blood_type,
            "created_at": str(p.created_at)
        } for p in patients]
    
    def get_patient_details(self, patient_id: Optional[int] = None, patient_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a patient"""
        if patient_id:
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        elif patient_name:
            names = patient_name.split()
            if len(names) >= 2:
                patient = self.db.query(Patient).filter(
                    and_(
                        Patient.first_name.ilike(f"%{names[0]}%"),
                        Patient.last_name.ilike(f"%{names[-1]}%")
                    )
                ).first()
            else:
                patient = self.db.query(Patient).filter(
                    or_(
                        Patient.first_name.ilike(f"%{patient_name}%"),
                        Patient.last_name.ilike(f"%{patient_name}%")
                    )
                ).first()
        else:
            return {"error": "Please provide patient_id or patient_name"}
        
        if not patient:
            return {"error": "Patient not found"}
        
        # Get appointments
        appointments = self.db.query(Appointment).filter(
            Appointment.patient_id == patient.id
        ).order_by(Appointment.appointment_date.desc()).limit(10).all()
        
        # Get billing history
        billings = self.db.query(Invoice).filter(
            Invoice.patient_id == patient.id
        ).order_by(Invoice.created_at.desc()).limit(10).all()
        
        return {
            "patient_info": {
                "id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "email": patient.email,
                "phone": patient.phone,
                "date_of_birth": str(patient.date_of_birth) if patient.date_of_birth else None,
                "age": patient.age if hasattr(patient, 'age') else None,
                "blood_type": patient.blood_type,
                "address": patient.address,
                "emergency_contact": patient.emergency_contact_name,
                "emergency_phone": patient.emergency_contact_phone,
                "created_at": str(patient.created_at)
            },
            "appointments": [{
                "id": apt.id,
                "date": str(apt.appointment_date),
                "reason": apt.reason,
                "status": apt.status,
                "doctor": apt.doctor.full_name if apt.doctor else None
            } for apt in appointments],
            "billing_history": [{
                "id": bill.id,
                "amount": float(bill.total_amount),
                "status": bill.status,
                "date": str(bill.created_at)
            } for bill in billings],
            "total_appointments": len(appointments),
            "total_billed": sum(float(b.total_amount) for b in billings)
        }
    
    def get_doctor_schedule(self, doctor_name: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get doctor's appointment schedule"""
        # Find doctor
        doctor = self.db.query(User).filter(
            and_(
                User.role == "doctor",
                User.full_name.ilike(f"%{doctor_name}%")
            )
        ).first()
        
        if not doctor:
            return {"error": f"Doctor '{doctor_name}' not found"}
        
        # Build query
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor.id)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        else:
            # Default to next 7 days
            query = query.filter(Appointment.appointment_date >= datetime.now())
            query = query.filter(Appointment.appointment_date <= datetime.now() + timedelta(days=7))
        
        appointments = query.order_by(Appointment.appointment_date).all()
        
        return {
            "doctor": {
                "id": doctor.id,
                "name": doctor.full_name,
                "prc_license": doctor.prc_license
            },
            "appointments": [{
                "id": apt.id,
                "date": str(apt.appointment_date),
                "patient": f"{apt.patient.first_name} {apt.patient.last_name}" if apt.patient else None,
                "reason": apt.reason,
                "status": apt.status
            } for apt in appointments],
            "total_appointments": len(appointments)
        }
    
    def get_financial_summary(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get financial summary (revenue, expenses, profit)"""
        # Default to current month
        if not date_from:
            date_from = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        
        # Revenue (Payments)
        revenue_query = self.db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.payment_date >= date_from,
                Payment.payment_date <= date_to,
                Payment.status == "completed"
            )
        )
        total_revenue = revenue_query.scalar() or 0
        
        # Expenses
        expense_query = self.db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.expense_date >= date_from,
                Expense.expense_date <= date_to
            )
        )
        total_expenses = expense_query.scalar() or 0
        
        # Doctor Payouts
        payout_query = self.db.query(func.sum(DoctorPayout.gross_amount)).filter(
            and_(
                DoctorPayout.period_start >= date_from,
                DoctorPayout.period_end <= date_to
            )
        )
        total_payouts = payout_query.scalar() or 0
        
        profit = float(total_revenue) - float(total_expenses) - float(total_payouts)
        
        return {
            "period": {
                "from": date_from,
                "to": date_to
            },
            "revenue": float(total_revenue),
            "expenses": float(total_expenses),
            "doctor_payouts": float(total_payouts),
            "net_profit": profit,
            "profit_margin": (profit / float(total_revenue) * 100) if total_revenue > 0 else 0
        }
    
    def get_appointment_stats(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get appointment statistics"""
        query = self.db.query(Appointment)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        total = query.count()
        completed = query.filter(Appointment.status == "completed").count()
        cancelled = query.filter(Appointment.status == "cancelled").count()
        pending = query.filter(Appointment.status == "scheduled").count()
        
        return {
            "total_appointments": total,
            "completed": completed,
            "cancelled": cancelled,
            "pending": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for AI"""
        return [
            {
                "name": "get_patient_count",
                "description": "Get total number of patients, optionally filtered by date range",
                "parameters": {
                    "filters": "Optional dict with 'date_from' and 'date_to' keys"
                }
            },
            {
                "name": "search_patients",
                "description": "Search for patients by name, email, or phone number",
                "parameters": {
                    "search_term": "Name, email, or phone to search for",
                    "limit": "Maximum number of results (default 10)"
                }
            },
            {
                "name": "get_patient_details",
                "description": "Get complete information about a specific patient including appointments and billing",
                "parameters": {
                    "patient_id": "Patient ID (optional)",
                    "patient_name": "Patient name (optional)"
                }
            },
            {
                "name": "get_doctor_schedule",
                "description": "Get a doctor's appointment schedule",
                "parameters": {
                    "doctor_name": "Doctor's name",
                    "date_from": "Start date (optional)",
                    "date_to": "End date (optional)"
                }
            },
            {
                "name": "get_financial_summary",
                "description": "Get financial summary including revenue, expenses, and profit",
                "parameters": {
                    "date_from": "Start date (optional, defaults to current month)",
                    "date_to": "End date (optional, defaults to today)"
                }
            },
            {
                "name": "get_appointment_stats",
                "description": "Get appointment statistics (total, completed, cancelled, pending)",
                "parameters": {
                    "date_from": "Start date (optional)",
                    "date_to": "End date (optional)"
                }
            }
        ]


class AIAssistant:
    """
    AI Assistant that can answer questions about the database
    Supports both OpenAI (online) and local Phi-3 (offline) modes
    """

    def __init__(self, db: Session):
        self.db = db
        self.tools = DatabaseQueryTools(db)
        self.conversation_history: List[Dict[str, str]] = []

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI"""
        return """You are MediFlow AI Assistant, a helpful database assistant for a Philippine hospital management system.

Your ONLY purpose is to help users query and understand data in the MediFlow database. You can answer questions about:
- Patients (count, search, details, medical history)
- Doctors (schedules, appointments, availability)
- Appointments (statistics, schedules, status)
- Financial data (revenue, expenses, profit, billing)
- Hospital operations (statistics, summaries)

IMPORTANT RULES:
1. You MUST ONLY answer questions about data in the MediFlow system
2. DO NOT answer general medical questions (e.g., "What is diabetes?", "How to treat fever?")
3. DO NOT provide medical advice or diagnoses
4. If asked a general question, politely redirect: "I can only help with MediFlow database queries. For medical information, please consult a healthcare professional or use ChatGPT/Claude."
5. Always use the provided tools to query the database
6. Be concise and factual
7. Format numbers clearly (use commas for thousands)
8. Always mention the date range when showing financial data

Available tools:
- get_patient_count: Count total patients
- search_patients: Find patients by name/email/phone
- get_patient_details: Get complete patient information
- get_doctor_schedule: View doctor's appointments
- get_financial_summary: Get revenue, expenses, profit
- get_appointment_stats: Get appointment statistics

Example good questions:
- "How many patients do we have?"
- "Show me details for patient Maria Santos"
- "What is Dr. Cruz's schedule this week?"
- "What's our revenue this month?"
- "How many appointments were completed today?"

Example bad questions (redirect these):
- "What is diabetes?" → "I can only help with MediFlow data. Please use ChatGPT for medical information."
- "How to treat fever?" → "I'm a database assistant, not a medical advisor. Please consult a doctor."
"""

    async def chat(self, user_message: str, use_local: bool = False) -> Dict[str, Any]:
        """
        Process a chat message and return AI response

        Args:
            user_message: User's question
            use_local: Force use of local LLM (for offline mode)

        Returns:
            Dict with response, tool_calls, and metadata
        """
        # Check if question is about database or general knowledge
        if self._is_general_question(user_message):
            return {
                "response": "I'm MediFlow AI Assistant, designed specifically to help you query the hospital database. I can answer questions about patients, doctors, appointments, and financials in your system.\n\nFor general medical questions or health information, please use ChatGPT, Claude, or consult with a healthcare professional.\n\nHow can I help you with your MediFlow data today?",
                "tool_calls": [],
                "model_used": "rule_based",
                "is_database_query": False
            }

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Keep only last N messages
        if len(self.conversation_history) > settings.ai_max_context_messages * 2:
            self.conversation_history = self.conversation_history[-settings.ai_max_context_messages * 2:]

        # Try OpenAI first (if online and not forced local)
        if not use_local and settings.openai_api_key:
            try:
                response = await self._chat_with_openai(user_message)
                response["model_used"] = "openai"
                return response
            except Exception as e:
                if settings.ai_fallback_to_local and settings.local_llm_enabled:
                    print(f"OpenAI failed, falling back to local LLM: {e}")
                    response = await self._chat_with_local_llm(user_message)
                    response["model_used"] = "local_phi3_fallback"
                    return response
                else:
                    raise

        # Use local LLM
        if settings.local_llm_enabled:
            response = await self._chat_with_local_llm(user_message)
            response["model_used"] = "local_phi3"
            return response

        # No AI available
        return {
            "response": "AI assistant is not configured. Please set up OpenAI API key or enable local LLM.",
            "tool_calls": [],
            "model_used": "none",
            "error": "No AI backend available"
        }

    def _is_general_question(self, message: str) -> bool:
        """Check if question is general medical/health question (not database query)"""
        message_lower = message.lower()

        # Keywords that indicate general questions
        general_keywords = [
            "what is", "what are", "how to treat", "how to cure", "symptoms of",
            "causes of", "diagnosis of", "medicine for", "drug for", "treatment for",
            "how does", "why does", "explain", "tell me about", "information about",
            "diabetes", "hypertension", "fever", "cough", "headache", "disease",
            "infection", "virus", "bacteria", "cancer", "heart attack", "stroke"
        ]

        # Keywords that indicate database queries
        database_keywords = [
            "how many", "count", "total", "list", "show", "find", "search",
            "patient", "doctor", "appointment", "schedule", "revenue", "expense",
            "profit", "billing", "payment", "financial", "today", "this week",
            "this month", "yesterday", "last", "our", "we have", "in our system"
        ]

        # Check for general keywords
        has_general = any(keyword in message_lower for keyword in general_keywords)

        # Check for database keywords
        has_database = any(keyword in message_lower for keyword in database_keywords)

        # If has general keywords but no database keywords, it's a general question
        return has_general and not has_database

    async def _chat_with_openai(self, user_message: str) -> Dict[str, Any]:
        """Chat using OpenAI API"""
        try:
            import openai
            openai.api_key = settings.openai_api_key

            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ] + self.conversation_history

            # TODO: Implement function calling with tools
            # For now, simple chat completion
            response = await openai.ChatCompletion.acreate(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.ai_temperature,
                max_tokens=settings.openai_max_tokens
            )

            assistant_message = response.choices[0].message.content

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return {
                "response": assistant_message,
                "tool_calls": [],
                "is_database_query": True
            }

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _chat_with_local_llm(self, user_message: str) -> Dict[str, Any]:
        """Chat using local Phi-3 model via llama.cpp"""
        try:
            from llama_cpp import Llama

            # Load model (cache it in production)
            if not hasattr(self, '_local_model'):
                self._local_model = Llama(
                    model_path=settings.local_llm_model_path,
                    n_ctx=settings.local_llm_context_size,
                    n_threads=settings.local_llm_threads
                )

            # Build prompt
            prompt = f"{self._get_system_prompt()}\n\nUser: {user_message}\nAssistant:"

            # Generate response
            response = self._local_model(
                prompt,
                max_tokens=settings.openai_max_tokens,
                temperature=settings.ai_temperature,
                stop=["User:", "\n\n"]
            )

            assistant_message = response['choices'][0]['text'].strip()

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return {
                "response": assistant_message,
                "tool_calls": [],
                "is_database_query": True
            }

        except Exception as e:
            raise Exception(f"Local LLM error: {str(e)}")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

