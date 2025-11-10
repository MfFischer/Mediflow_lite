# 🤖 AI Assistant Testing Guide

## Overview
MediFlow's AI Assistant is a **database-focused** intelligent query system that works both **online** (OpenAI) and **offline** (local Phi-3 model). It's designed specifically for Philippine hospitals with unreliable internet connectivity.

---

## ✅ Prerequisites

### 1. **Backend Running**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. **Frontend Running**
```bash
cd frontend
npx next dev -p 3005
```

### 3. **User Account**
- You must be logged in to use the AI Assistant
- Any user role can access the AI Assistant
- Different roles see different data based on RBAC permissions

---

## 🎯 What the AI Assistant Does

### ✅ **WILL Answer:**
- "How many patients do we have?"
- "Show me Dr. Cruz's schedule this week"
- "What's our revenue this month?"
- "Find patient named Maria Santos"
- "How many appointments today?"
- "What are our expenses for January?"
- "Show me all pending invoices"
- "Who are the doctors with appointments tomorrow?"

### ❌ **WILL NOT Answer:**
- "What is diabetes?" (general medical question)
- "How to treat hypertension?" (medical advice)
- "What are the symptoms of COVID-19?" (health information)
- "Recommend a treatment for fever" (medical recommendation)

**Why?** The AI is designed to query YOUR hospital's database, not provide general medical information. For medical questions, users should consult ChatGPT, Claude, or medical professionals.

---

## 🧪 Testing Steps

### **Step 1: Access the AI Assistant**
1. Open browser: http://localhost:3005
2. Login with your credentials
3. Navigate to **AI Assistant** page (in navigation menu)

### **Step 2: Check AI Status**
Look at the top-right corner of the chat interface:
- **🟢 Online** - OpenAI is available
- **🔴 Offline** - Using local Phi-3 model
- **Toggle Switch** - "Use Local AI" to force offline mode

### **Step 3: Test Database Queries**

#### **Test 1: Patient Count**
**Query:** "How many patients do we have?"

**Expected Response:**
```
We currently have X patients in the system.
```

#### **Test 2: Patient Search**
**Query:** "Find patient named Maria"

**Expected Response:**
```
Found 2 patients matching "Maria":
1. Maria Santos (ID: 123) - maria@example.com
2. Maria Cruz (ID: 456) - maria.cruz@example.com
```

#### **Test 3: Doctor Schedule**
**Query:** "Show me Dr. Cruz's schedule this week"

**Expected Response:**
```
Dr. Cruz has 5 appointments this week:
- Monday 9:00 AM: Patient John Doe (Checkup)
- Tuesday 2:00 PM: Patient Jane Smith (Follow-up)
...
```

#### **Test 4: Financial Query** (Admin/Accountant only)
**Query:** "What's our revenue this month?"

**Expected Response:**
```
Revenue for November 2025:
- Total Revenue: ₱150,000
- Total Expenses: ₱80,000
- Net Profit: ₱70,000
```

**Note:** If you're not Admin/Accountant, you'll get:
```
I don't have permission to access financial data. Please contact an administrator.
```

#### **Test 5: Appointment Statistics**
**Query:** "How many appointments do we have today?"

**Expected Response:**
```
Today's appointments:
- Total: 12 appointments
- Completed: 5
- Scheduled: 7
- Cancelled: 0
```

### **Step 4: Test Rejection of General Questions**

#### **Test 6: General Medical Question**
**Query:** "What is diabetes?"

**Expected Response:**
```
I'm MediFlow AI Assistant, designed to help you query the hospital database. 
For medical information, please use ChatGPT or consult a healthcare professional.
```

#### **Test 7: Treatment Advice**
**Query:** "How to treat fever?"

**Expected Response:**
```
I'm MediFlow AI Assistant, designed to help you query the hospital database. 
For medical information, please use ChatGPT or consult a healthcare professional.
```

### **Step 5: Test Offline Mode**

1. **Toggle "Use Local AI"** switch to ON
2. **Wait 2-3 seconds** for the model to load (first time only)
3. **Ask a database query:** "How many patients do we have?"
4. **Verify response** comes from local Phi-3 model

**Expected Behavior:**
- Response may be slightly slower (2-5 seconds)
- Response quality should be similar to online mode
- No internet required!

### **Step 6: Test Conversation History**

1. Ask: "How many patients do we have?"
2. Ask: "What about appointments?"
3. Ask: "And revenue?"

**Expected Behavior:**
- AI remembers context from previous messages
- Can reference earlier parts of the conversation
- History limited to last 10 messages

### **Step 7: Test Clear History**

1. Have a conversation with multiple messages
2. Click **"Clear History"** button
3. Verify all messages are cleared
4. Start a new conversation

---

## 🔧 Configuration

### **Online Mode (OpenAI)**
Edit `backend/.env`:
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
```

### **Offline Mode (Local Phi-3)**
Edit `backend/.env`:
```env
LOCAL_LLM_ENABLED=true
LOCAL_LLM_MODEL_PATH=models/phi-3-mini-4k-instruct-q4.gguf
LOCAL_LLM_CONTEXT_SIZE=4096
LOCAL_LLM_THREADS=4
```

### **Auto-Fallback**
```env
AI_FALLBACK_TO_LOCAL=true
```
When enabled, if OpenAI fails (no internet, API error), automatically switches to local model.

---

## 🐛 Troubleshooting

### **Problem: "AI Assistant is unavailable"**
**Solution:**
1. Check backend is running: http://localhost:8000/docs
2. Check AI status endpoint: http://localhost:8000/api/v1/ai/status
3. Verify Phi-3 model exists: `backend/models/phi-3-mini-4k-instruct-q4.gguf`

### **Problem: "Permission denied" for financial queries**
**Solution:**
- Financial queries require Admin or Accountant role
- Login with appropriate user role
- Check user role in database

### **Problem: Slow responses in offline mode**
**Solution:**
1. Increase threads in `.env`: `LOCAL_LLM_THREADS=8`
2. Use a smaller model (Q4 is already optimized)
3. Ensure sufficient RAM (4GB+ recommended)

### **Problem: Model not found**
**Solution:**
```bash
cd backend
python download_phi3.py
```

---

## 📊 Performance Benchmarks

### **Online Mode (OpenAI GPT-4o-mini)**
- Response Time: 1-3 seconds
- Cost: ~$0.0001 per query
- Requires: Internet connection

### **Offline Mode (Phi-3 Q4)**
- Response Time: 2-5 seconds (first query), 1-3 seconds (subsequent)
- Cost: FREE
- Requires: 4GB RAM, 2.3GB disk space

---

## 🎯 Success Criteria

✅ **AI Assistant is working correctly if:**
1. Database queries return accurate results
2. General medical questions are rejected
3. Offline mode works without internet
4. RBAC permissions are enforced
5. Conversation history is maintained
6. Clear history button works
7. Online/offline toggle works
8. Error messages are clear and helpful

---

## 🚀 Next Steps

After testing:
1. **Add more test data** to database (patients, appointments, invoices)
2. **Test with different user roles** (Doctor, Nurse, Receptionist)
3. **Test edge cases** (empty database, invalid queries)
4. **Monitor performance** (response times, accuracy)
5. **Collect user feedback** (what queries are most useful?)

---

## 📝 Notes

- The AI uses **structured logging** - check `backend/logs/` for detailed logs
- All queries are **audited** - check audit_events table
- **Request IDs** are tracked for debugging
- **Slow queries** (>1 second) are automatically logged

---

**Happy Testing! 🎉**

