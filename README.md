# Microsoft Certification Practice Assessments - AI Voice Assistant

An AI-powered voice assistant application that crawls Microsoft Learn practice assessments and provides an interactive, hands-free learning experience with text-to-speech capabilities.

## Features

- 🎯 **Automated Web Crawling**: Extracts practice questions from Microsoft Learn certification assessments
- 🗣️ **Azure Speech Service**: Text-to-speech functionality for hands-free learning
- 🤖 **AI Agent**: Smart question management and automatic progression
- 📱 **Responsive UI**: Modern React frontend with intuitive controls
- 🔄 **Auto-progression**: Automatically moves to next question without manual intervention
- 📊 **Progress Tracking**: Monitors learning progress and performance

## Architecture

```
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── models/   # Data models
│   │   ├── services/ # Business logic
│   │   ├── routers/  # API endpoints
│   │   └── core/     # Configuration
│   └── requirements.txt
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── package.json
└── docs/            # Documentation
```

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Azure Speech Service**: Text-to-speech conversion
- **BeautifulSoup4**: Web scraping
- **Pydantic**: Data validation
- **uvicorn**: ASGI server

### Frontend
- **React**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client
- **Material-UI**: Component library
- **React Router**: Navigation

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Azure Speech Service subscription

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ms-cert-exam-practice-questions
```

2. Set up backend
```bash
cd backend
pip install -r requirements.txt
```

3. Set up frontend
```bash
cd frontend
npm install
```

4. Configure environment variables
```bash
# Create .env file in backend directory
AZURE_SPEECH_KEY=your_speech_service_key
AZURE_SPEECH_REGION=your_speech_service_region
```

### Running the Application

1. Start the backend
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend
```bash
cd frontend
npm start
```

## Available Certifications

The application supports practice assessments for 50+ Microsoft certifications including:
- Azure Fundamentals (AZ-900)
- Azure Administrator (AZ-104)
- Azure Developer (AZ-204)
- Azure Solutions Architect (AZ-305)
- Azure DevOps (AZ-400)
- Azure Security (AZ-500)
- And many more...

## License

MIT License