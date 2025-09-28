import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Home } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { AppState } from '../types';

interface SummaryPageProps {
  appState: AppState;
  updateAppState: (updates: Partial<AppState>) => void;
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

const SummaryPage: React.FC<SummaryPageProps> = ({ appState, updateAppState, onError, onSuccess }) => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  // Avoid unused variable warnings
  console.log('SummaryPage props:', { appState, updateAppState, onError, onSuccess });

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Assessment Summary
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Home />}
            onClick={() => navigate('/')}
          >
            Return to Home
          </Button>
        </Box>
        
        <Typography variant="body1" sx={{ mb: 2 }}>
          Summary for session {sessionId}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This page will show detailed results, analytics, and recommendations.
        </Typography>
      </Paper>
    </Box>
  );
};

export default SummaryPage;