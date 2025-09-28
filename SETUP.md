# Installation and Setup Instructions

## Backend Setup (FastAPI)

### Prerequisites
- Python 3.9 or higher
- Azure Speech Service subscription key and region

### Installation Steps

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env and add your Azure Speech Service credentials:
   # AZURE_SPEECH_KEY=your_azure_speech_service_key
   # AZURE_SPEECH_REGION=your_azure_speech_service_region
   ```

6. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 6000
   ```

The backend API will be available at: http://localhost:6000

API Documentation: http://localhost:6000/docs (when DEBUG=True)

## Frontend Setup (React)

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager

### Installation Steps

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # The default settings should work for local development
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

The frontend application will be available at: http://localhost:3001

## Azure Speech Service Setup

### Required Azure Resources

1. **Create an Azure Speech Service resource:**
   - Go to the Azure Portal (https://portal.azure.com)
   - Create a new "Speech" resource
   - Choose your subscription and resource group
   - Select a region (e.g., East US, West Europe)
   - Choose the pricing tier (F0 for free tier)

2. **Get the credentials:**
   - After deployment, go to your Speech Service resource
   - Navigate to "Keys and Endpoint"
   - Copy one of the keys and the region
   - Add these to your backend `.env` file

### Speech Service Configuration

The application uses the following default settings:
- **Voice**: en-US-JennyNeural (can be changed in settings)
- **Audio Format**: MP3, 16 kHz, 32 kbit/s mono
- **Speech Rate**: Normal (0%)
- **Speech Pitch**: Normal (0%)

## Testing the Setup

### Backend Testing

1. **Test the API health:**
   ```bash
   curl http://localhost:6000/health
   ```

2. **Test Azure Speech Service:**
   ```bash
   curl http://localhost:6000/api/v1/audio/test
   ```

3. **Get available certifications:**
   ```bash
   curl http://localhost:6000/api/v1/assessments/certifications
   ```

### Frontend Testing

1. Open http://localhost:3001 in your browser
2. You should see the home page with available certifications
3. Click on a certification to start a practice assessment

## Troubleshooting

### Common Issues

1. **Azure Speech Service connection fails:**
   - Verify your AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in the .env file
   - Check that your Azure subscription is active
   - Ensure the Speech Service resource is deployed correctly

2. **Frontend can't connect to backend:**
   - Make sure the backend is running on port 6000
   - Check the REACT_APP_API_BASE_URL in frontend/.env
   - Verify CORS settings in the backend

3. **Audio playback issues:**
   - Check browser permissions for audio playback
   - Verify the audio cache directory exists and is writable
   - Test with different browsers

4. **Web scraping fails:**
   - Microsoft Learn practice assessments may have changed structure
   - The application falls back to sample data when scraping fails
   - Check network connectivity and firewall settings

### Development Mode

For development, you can run both services simultaneously:

1. **Terminal 1 (Backend):**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   uvicorn app.main:app --reload
   ```

2. **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm start
   ```

## Production Deployment

### Backend Deployment

1. **Set production environment variables:**
   ```bash
   DEBUG=False
   SECRET_KEY=your_secure_secret_key
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

### Frontend Deployment

1. **Build the production version:**
   ```bash
   npm run build
   ```

2. **Serve the built files:**
   The `build` directory contains the static files ready for deployment.

### Azure Deployment

Both the backend and frontend can be deployed to Azure:

- **Backend**: Azure App Service (Python), Azure Container Instances, or Azure Kubernetes Service
- **Frontend**: Azure Static Web Apps, Azure App Service, or Azure Blob Storage with CDN

Refer to the deployment documentation for detailed Azure deployment instructions.