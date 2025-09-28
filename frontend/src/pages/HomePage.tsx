import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AppState, CertificationInfo } from '../types';

interface HomePageProps {
  appState: AppState;
  updateAppState: (updates: Partial<AppState>) => void;
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({
  appState,
  updateAppState,
  onError,
  onSuccess,
}) => {
  const navigate = useNavigate();
  const [certifications, setCertifications] = useState<CertificationInfo[]>([]);
  const [loading, setLoading] = useState(true);

  // Complete certification data from Microsoft Learn (50 available practice assessments)
  const mockCertifications: CertificationInfo[] = [
    // Azure AI
    { code: 'AI-102', title: 'Designing and Implementing a Microsoft Azure AI Solution', category: 'Azure AI', level: 'Associate' },
    { code: 'AI-900', title: 'Microsoft Azure AI Fundamentals', category: 'Azure AI', level: 'Fundamentals' },
    
    // Azure Core
    { code: 'AZ-104', title: 'Microsoft Azure Administrator', category: 'Azure', level: 'Associate' },
    { code: 'AZ-140', title: 'Configuring and Operating Microsoft Azure Virtual Desktop', category: 'Azure', level: 'Associate' },
    { code: 'AZ-204', title: 'Developing Solutions for Microsoft Azure', category: 'Azure', level: 'Associate' },
    { code: 'AZ-305', title: 'Designing Microsoft Azure Infrastructure Solutions', category: 'Azure', level: 'Expert' },
    { code: 'AZ-400', title: 'Designing and Implementing Microsoft DevOps Solutions', category: 'Azure', level: 'Expert' },
    { code: 'AZ-500', title: 'Microsoft Azure Security Technologies', category: 'Azure', level: 'Associate' },
    { code: 'AZ-700', title: 'Designing and Implementing Microsoft Azure Networking Solutions', category: 'Azure', level: 'Associate' },
    { code: 'AZ-800', title: 'Administering Windows Server Hybrid Core Infrastructure', category: 'Azure', level: 'Associate' },
    { code: 'AZ-801', title: 'Configuring Windows Server Hybrid Advanced Services', category: 'Azure', level: 'Associate' },
    { code: 'AZ-900', title: 'Microsoft Azure Fundamentals', category: 'Azure', level: 'Fundamentals' },
    
    // Data & Analytics
    { code: 'DP-100', title: 'Designing and Implementing a Data Science Solution on Azure', category: 'Data & Analytics', level: 'Associate' },
    { code: 'DP-300', title: 'Administering Microsoft Azure SQL Solutions', category: 'Data & Analytics', level: 'Associate' },
    { code: 'DP-420', title: 'Azure Cosmos DB Developer Specialty', category: 'Data & Analytics', level: 'Specialty' },
    { code: 'DP-600', title: 'Implementing Analytics Solutions Using Microsoft Fabric', category: 'Data & Analytics', level: 'Associate' },
    { code: 'DP-700', title: 'Microsoft Certified: Fabric Data Engineer Associate', category: 'Data & Analytics', level: 'Associate' },
    { code: 'DP-900', title: 'Microsoft Azure Data Fundamentals', category: 'Data & Analytics', level: 'Fundamentals' },
    
    // GitHub
    { code: 'GH-100', title: 'GitHub Administration', category: 'GitHub', level: 'Associate' },
    { code: 'GH-200', title: 'GitHub Actions', category: 'GitHub', level: 'Associate' },
    { code: 'GH-300', title: 'GitHub Copilot', category: 'GitHub', level: 'Associate' },
    { code: 'GH-500', title: 'GitHub Advanced Security', category: 'GitHub', level: 'Associate' },
    { code: 'GH-900', title: 'GitHub Foundations', category: 'GitHub', level: 'Fundamentals' },
    
    // Dynamics 365
    { code: 'MB-230', title: 'Microsoft Dynamics 365 Customer Service Functional Consultant', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-240', title: 'Microsoft Dynamics 365 Field Service Functional Consultant', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-280', title: 'Dynamics 365 Customer Experience Analyst Associate', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-310', title: 'Microsoft Dynamics 365 Finance Functional Consultant', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-330', title: 'Microsoft Dynamics 365 Supply Chain Management Functional Consultant Associate', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-335', title: 'Microsoft Dynamics 365 Supply Chain Management Functional Consultant Expert', category: 'Dynamics 365', level: 'Expert' },
    { code: 'MB-500', title: 'Dynamics 365: Finance and Operations Apps Developer Associate', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-800', title: 'Microsoft Dynamics 365 Business Central Functional Consultant Associate', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-820', title: 'Microsoft Dynamics 365 Business Central Developer Associate', category: 'Dynamics 365', level: 'Associate' },
    { code: 'MB-910', title: 'Microsoft Dynamics 365 Fundamentals (CRM)', category: 'Dynamics 365', level: 'Fundamentals' },
    { code: 'MB-920', title: 'Microsoft Dynamics 365 Fundamentals (ERP)', category: 'Dynamics 365', level: 'Fundamentals' },
    
    // Microsoft 365
    { code: 'MD-102', title: 'Endpoint Administrator', category: 'Microsoft 365', level: 'Associate' },
    { code: 'MS-102', title: 'Microsoft 365 Administrator', category: 'Microsoft 365', level: 'Expert' },
    { code: 'MS-700', title: 'Managing Microsoft Teams', category: 'Microsoft 365', level: 'Associate' },
    { code: 'MS-721', title: 'Collaboration Communications Systems Engineer', category: 'Microsoft 365', level: 'Associate' },
    { code: 'MS-900', title: 'Microsoft 365 Fundamentals', category: 'Microsoft 365', level: 'Fundamentals' },
    
    // Power Platform
    { code: 'PL-200', title: 'Microsoft Power Platform Functional Consultant', category: 'Power Platform', level: 'Associate' },
    { code: 'PL-300', title: 'Microsoft Power BI Data Analyst', category: 'Power Platform', level: 'Associate' },
    { code: 'PL-400', title: 'Microsoft Power Platform Developer', category: 'Power Platform', level: 'Associate' },
    { code: 'PL-500', title: 'Microsoft Power Automate RPA Developer', category: 'Power Platform', level: 'Associate' },
    { code: 'PL-600', title: 'Microsoft Power Platform Solution Architect', category: 'Power Platform', level: 'Expert' },
    { code: 'PL-900', title: 'Microsoft Power Platform Fundamentals', category: 'Power Platform', level: 'Fundamentals' },
    
    // Security, Compliance & Identity
    { code: 'SC-100', title: 'Microsoft Cybersecurity Architect', category: 'Security', level: 'Expert' },
    { code: 'SC-200', title: 'Microsoft Security Operations Analyst', category: 'Security', level: 'Associate' },
    { code: 'SC-300', title: 'Microsoft Identity and Access Administrator', category: 'Security', level: 'Associate' },
    { code: 'SC-401', title: 'Microsoft Certified: Information Security Administrator Associate', category: 'Security', level: 'Associate' },
    { code: 'SC-900', title: 'Microsoft Security, Compliance, and Identity Fundamentals', category: 'Security', level: 'Fundamentals' },
  ];

  useEffect(() => {
    // Simulate loading certifications
    const loadCertifications = async () => {
      try {
        setLoading(true);
        // In a real app, this would call assessmentApi.getCertifications()
        setTimeout(() => {
          setCertifications(mockCertifications);
          setLoading(false);
          onSuccess('Certifications loaded successfully');
        }, 1000);
      } catch (error) {
        onError('Failed to load certifications');
        setLoading(false);
      }
    };

    loadCertifications();
  }, []);

  const handleSelectCertification = (certificationCode: string) => {
    navigate(`/assessment/${certificationCode}`);
  };

  const getLevelColor = (level?: string) => {
    switch (level) {
      case 'Fundamentals':
        return '#4caf50';
      case 'Associate':
        return '#ff9800';
      case 'Expert':
        return '#f44336';
      case 'Specialty':
        return '#9c27b0';
      default:
        return '#757575';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading certifications...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Microsoft Certification Practice
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          AI-powered voice assistant for hands-free learning
        </Typography>
        <Alert severity="info" sx={{ mt: 2, maxWidth: 600, mx: 'auto' }}>
          🎧 Use headphones for the best audio experience. The AI will read questions aloud and automatically progress through the assessment.
        </Alert>
      </Box>

      {/* Features */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🎤 Voice Assistant
                </Typography>
                <Typography variant="body2">
                  AI reads questions and explanations aloud for hands-free learning
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🤖 Auto Progression
                </Typography>
                <Typography variant="body2">
                  Automatically advances to the next question without manual clicking
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📊 Progress Tracking
                </Typography>
                <Typography variant="body2">
                  Track your performance and get personalized recommendations
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🎯 Adaptive Learning
                </Typography>
                <Typography variant="body2">
                  AI adjusts the experience based on your learning patterns
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Certifications */}
      <Box>
        <Typography variant="h5" gutterBottom>
          Choose a Certification to Practice
        </Typography>
        <Grid container spacing={3}>
          {certifications.map((cert) => (
            <Grid item xs={12} sm={6} md={4} key={cert.code}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
                  },
                }}
                onClick={() => handleSelectCertification(cert.code)}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h3">
                      {cert.code}
                    </Typography>
                    <Box
                      sx={{
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        backgroundColor: getLevelColor(cert.level),
                        color: 'white',
                        fontSize: '0.75rem',
                        fontWeight: 500,
                      }}
                    >
                      {cert.level}
                    </Box>
                  </Box>
                  <Typography variant="body1" gutterBottom>
                    {cert.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {cert.category}
                  </Typography>
                </CardContent>
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectCertification(cert.code);
                    }}
                  >
                    Start Practice Assessment
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Footer */}
      <Box sx={{ mt: 6, pt: 4, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Powered by Azure Speech Service and AI • Built with React and FastAPI
        </Typography>
      </Box>
    </Box>
  );
};

export default HomePage;