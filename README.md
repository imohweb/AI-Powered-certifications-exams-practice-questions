# AI-Powered Certification Practice Assessments - Voice Assistant

[![Deploy Backend](https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-backend.yml/badge.svg)](https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-backend.yml)
[![Deploy Frontend](https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source AI-powered voice assistant application that provides interactive, hands-free learning experiences for cloud certification exams with multilingual text-to-speech capabilities.

> **🌟 Open Source Project** - We welcome contributions! Currently supporting Microsoft Azure certifications, with plans to expand to AWS and Google Cloud Platform.

## 📋 Table of Contents
- [Features](#features)
- [Supported Platforms](#supported-platforms)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🎯 **Automated Web Crawling**: Extracts practice questions from certification provider learning platforms
- 🗣️ **Azure Speech Service**: Multilingual text-to-speech functionality for hands-free learning
- 🌍 **Multilingual Support**: Practice in multiple languages with voice synthesis
- 🤖 **AI Agent**: Smart question management and automatic progression
- 📱 **Responsive UI**: Modern React frontend with intuitive voice and mouse controls
- 🔄 **Voice Commands**: Navigate, check answers, and control reading with voice
- 📊 **Progress Tracking**: Monitors learning progress and performance
- ♿ **Accessibility**: Voice-enabled learning for enhanced accessibility

## Supported Platforms

### Currently Available
- ✅ **Microsoft Azure** - 50+ certification practice assessments

### Coming Soon (Contributions Welcome!)
- � **Amazon Web Services (AWS)** - Looking for contributors to add official AWS practice questions
- 🔜 **Google Cloud Platform (GCP)** - Looking for contributors to add official GCP practice questions

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
- **Azure Speech Service**: Multilingual text-to-speech conversion
- **Azure Translator**: Multi-language translation service
- **BeautifulSoup4**: Web scraping
- **Pydantic**: Data validation
- **uvicorn**: ASGI server (Asynchronous Server Gateway Interface)

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
git clone https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions.git
cd AI-Powered-certifications-exams-practice-questions
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
AZURE_TRANSLATOR_KEY=your_translator_service_key
AZURE_TRANSLATOR_REGION=your_translator_service_region
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

## Deployment

### Production Deployment

The application is designed for production deployment with:
- **Backend**: Azure Container Apps
- **Frontend**: GitHub Pages

📚 **Deployment Documentation**:
- [Complete Deployment Guide](docs/DEPLOYMENT.md) - Detailed deployment instructions
- [Quick Deploy Guide](docs/QUICK_DEPLOY.md) - Quick reference for deployment

### Live Application

- **Frontend**: https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/
- **Backend**: Deployed on Azure Container Apps

### CI/CD Pipeline

Automated deployment via GitHub Actions:
- Backend automatically deploys to Azure Container Apps on push to `main`
- Frontend automatically deploys to GitHub Pages on push to `main`
- Docker images versioned with build numbers for easy rollback
- All secrets managed via GitHub Secrets (no hardcoded credentials)

## Available Certifications

### Microsoft Azure
The application currently supports practice assessments for 50+ Microsoft certifications including:
- Azure Fundamentals (AZ-900)
- Azure Administrator (AZ-104)
- Azure Developer (AZ-204)
- Azure Solutions Architect (AZ-305)
- Azure DevOps (AZ-400)
- Azure Security (AZ-500)
- And many more...

### AWS (Contributions Welcome!)
We're looking for contributors to add official AWS certification practice questions:
- AWS Certified Solutions Architect
- AWS Certified Developer
- AWS Certified SysOps Administrator
- And more...

### Google Cloud (Contributions Welcome!)
We're looking for contributors to add official GCP certification practice questions:
- Google Cloud Associate Cloud Engineer
- Google Cloud Professional Cloud Architect
- Google Cloud Professional Data Engineer
- And more...

## Contributing

We welcome contributions from the community! Whether you want to add practice questions for AWS, Google Cloud, fix bugs, or improve features, your help is appreciated.

### 🤝 How to Contribute

#### Repository Structure
- **Repository URL**: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions
- **Main Branch**: `main` - Production-ready code
- **Development Branch**: `develop` - Active development

#### Branch Protection Rules
⚠️ **Important**: Direct pushes to `main` and `develop` branches are not allowed. All changes must go through Pull Requests.

### Contribution Workflow

1. **Fork the Repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/AI-Powered-certifications-exams-practice-questions.git
   cd AI-Powered-certifications-exams-practice-questions
   ```

2. **Create a Feature Branch**
   
   Branch naming convention: `feature/yourfirstname`
   
   ```bash
   # Example: If your first name is John
   git checkout develop
   git pull origin develop
   git checkout -b feature/john
   ```

3. **Make Your Changes**
   
   Areas where you can contribute:
   - **Add AWS Practice Questions**: Create scrapers and database entries for AWS certifications
   - **Add GCP Practice Questions**: Create scrapers and database entries for GCP certifications
   - **Improve UI/UX**: Enhance the frontend interface
   - **Add Features**: Voice commands, accessibility improvements, etc.
   - **Fix Bugs**: Check issues for bug reports
   - **Documentation**: Improve README, add guides, or create tutorials

4. **Test Your Changes**
   
   ✅ **Pull requests will only be approved if the code is working correctly**
   
   ```bash
   # Test backend
   cd backend
   python -m pytest  # Run tests if available
   uvicorn app.main:app --reload  # Verify server runs
   
   # Test frontend
   cd frontend
   npm run build  # Ensure it builds without errors
   npm start  # Verify UI works correctly
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: Add AWS Solutions Architect practice questions"
   # Use conventional commit messages:
   # feat: New feature
   # fix: Bug fix
   # docs: Documentation changes
   # style: Code style changes
   # refactor: Code refactoring
   # test: Test additions/changes
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/yourfirstname
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select `develop` as the base branch
   - Select your `feature/yourfirstname` branch as the compare branch
   - Fill in the PR template with:
     - Description of changes
     - Testing performed
     - Screenshots (if UI changes)
     - Related issues

### 📝 Contribution Guidelines

#### For AWS/GCP Question Contributors

If you're adding practice questions for AWS or Google Cloud:

1. **Source Official Questions Only**
   - Use only official practice questions from AWS or GCP learning platforms
   - Document the source URL in your PR

2. **Follow Existing Data Structure**
   - Review the existing Microsoft Azure implementation
   - Match the database schema in `backend/app/models/`
   - Ensure question format is consistent

3. **Create Appropriate Scrapers**
   - Add scraper logic in `backend/app/services/`
   - Follow the pattern used for Microsoft Learn scraping
   - Handle errors gracefully

4. **Update Frontend**
   - Add certification logos/icons
   - Update certification selection UI
   - Ensure compatibility with existing voice features

5. **Test Thoroughly**
   - Verify questions load correctly
   - Test voice reading for all questions
   - Check multilingual support
   - Ensure navigation works properly

#### Code Quality Standards

- ✅ Code must run without errors
- ✅ Follow existing code style and patterns
- ✅ Add comments for complex logic
- ✅ Update documentation for new features
- ✅ Ensure TypeScript types are correct
- ✅ Test with multiple certifications

### 🐛 Reporting Issues

Found a bug or have a suggestion?

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Screenshots or error messages
   - Your environment (OS, browser, etc.)

### 💡 Feature Requests

Have an idea? Create an issue with:
- Feature description
- Use case and benefits
- Proposed implementation (optional)

### 📞 Need Help?

- Check existing documentation
- Review closed issues and PRs
- Open a discussion or issue for questions

## License

MIT License

Copyright (c) 2025 Imoh Etuk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

- Microsoft Learn for official practice assessments
- Azure AI Services for speech and translation capabilities
- All contributors who help expand this project to AWS and GCP

## 📊 Project Stats

![GitHub Stars](https://img.shields.io/github/stars/imohweb/AI-Powered-certifications-exams-practice-questions)
![GitHub Forks](https://img.shields.io/github/forks/imohweb/AI-Powered-certifications-exams-practice-questions)
![GitHub Issues](https://img.shields.io/github/issues/imohweb/AI-Powered-certifications-exams-practice-questions)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/imohweb/AI-Powered-certifications-exams-practice-questions)
![License](https://img.shields.io/github/license/imohweb/AI-Powered-certifications-exams-practice-questions)

---

**Made with ❤️ by the community | Powered by Azure AI Services**