# Test Scripts

This folder contains test scripts for validating the backend API functionality.

## 📋 Available Test Scripts

### 1. `test_api_endpoints.py`
**Purpose:** Test the backend API endpoints to verify 50-question generation is working correctly.

**What it tests:**
- `/api/v1/assessments/certifications` - List available certifications
- `/api/v1/assessments/{cert_code}` - Generate practice assessment with 50 questions

**How to run:**
```bash
# Start the backend server first
cd backend
source venv/bin/activate
python main.py

# In another terminal, run the test
cd backend/test-scripts
python test_api_endpoints.py
```

**Expected output:**
- List of available certifications
- Successfully generated assessment with 50 questions
- Sample question and answer details

---

### 2. `test_frontend_api.py`
**Purpose:** Test the API endpoints that the frontend uses for multilingual audio and feedback.

**What it tests:**
- `/api/v1/audio/generate/multilingual` - Multilingual question audio
- `/api/v1/audio/generate/feedback` - Feedback audio in different languages

**How to run:**
```bash
# Start the backend server first
cd backend
source venv/bin/activate
python main.py

# In another terminal, run the test
cd backend/test-scripts
python test_frontend_api.py
```

**Expected output:**
- Audio URLs for questions in multiple languages (en, es, fr, de)
- Feedback audio URLs for correct/incorrect answers
- Duration information for each audio file

---

### 3. `test_azure_integration.py`
**Purpose:** Verify Azure Speech Service and Azure OpenAI integration.

**What it tests:**
- Azure Speech Service (text-to-speech functionality)
- Azure OpenAI Service (question generation)
- Azure Translator Service (if configured)

**How to run:**
```bash
cd backend
source venv/bin/activate
cd test-scripts
python test_azure_integration.py
```

**Expected output:**
- Azure Speech Service working confirmation
- Sample audio generation (bytes count)
- Azure OpenAI question generation test
- Sample generated question

**Note:** Requires Azure credentials to be configured in `.env` file:
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`

---

### 4. `test_50_questions.py`
**Purpose:** Test the enhanced AI question generator with 50 questions per assessment.

**What it tests:**
- Generation of exactly 50 questions for a certification
- Question quality (difficulty distribution, topic coverage)
- Estimated duration calculation
- Sample question format and structure

**How to run:**
```bash
cd backend
source venv/bin/activate
cd test-scripts
python test_50_questions.py
```

**Expected output:**
- Assessment with exactly 50 questions
- Difficulty distribution (Beginner, Intermediate, Advanced)
- Topic coverage statistics
- Sample question details

**Note:** This test may take 30-60 seconds as it generates 50 AI-powered questions.

---

### 5. `test_ai_generator.py`
**Purpose:** Test the AI question generator across multiple certification types.

**What it tests:**
- Question generation for various certifications:
  - AZ-900 (Azure Fundamentals)
  - MS-900 (Microsoft 365 Fundamentals)
  - PL-900 (Power Platform Fundamentals)
  - SC-900 (Security Fundamentals)
  - DP-900 (Data Fundamentals)

**How to run:**
```bash
cd backend
source venv/bin/activate
cd test-scripts
python test_ai_generator.py
```

**Expected output:**
- Success rate across all tested certifications
- Question count for each certification
- Difficulty distribution
- Pass/fail summary

**Note:** This test may take several minutes as it generates questions for multiple certifications.

---

## 🚀 Quick Start

### Prerequisites
1. Backend server running (for API tests)
2. Python virtual environment activated
3. Azure credentials configured (for Azure integration tests)

### Running All Tests
```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Start backend server
python main.py

# In another terminal, run tests
cd backend/test-scripts
python test_api_endpoints.py
python test_frontend_api.py
python test_azure_integration.py
python test_50_questions.py
python test_ai_generator.py
```

---

## 📝 Test Categories

### API Tests
- `test_api_endpoints.py`
- `test_frontend_api.py`

### Azure Service Tests
- `test_azure_integration.py`

### AI Generator Tests
- `test_50_questions.py`
- `test_ai_generator.py`

---

## 🔧 Troubleshooting

### "Connection refused" error
**Problem:** Backend server is not running  
**Solution:** Start the backend server first with `python main.py`

### "Azure credentials not configured" error
**Problem:** Missing Azure service credentials  
**Solution:** Check your `.env` file has all required Azure credentials:
```env
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=your-region
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=your-openai-endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### "Module not found" error
**Problem:** Python path or dependencies issue  
**Solution:** 
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Tests take too long
**Problem:** AI generation can be slow  
**Solution:** This is normal for tests that generate questions. Test generation of 50 questions can take 30-60 seconds per certification.

---

## 📚 Related Documentation

- [Backend API Documentation](../app/README.md) - API reference
- [Deployment Guide](../../docs/DEPLOYMENT.md) - Deployment instructions
- [Environment Setup](../../docs/SETUP.md) - Environment configuration

---

**Last Updated:** 7 October 2025  
**Maintained by:** Development Team
