import React, { useState, useCallback } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Alert,
  Snackbar,
} from '@mui/material';
import { AppState } from './types';
import HomePage from './pages/HomePage';
import AssessmentPage from './pages/AssessmentPage';
import SummaryPage from './pages/SummaryPage';

const App = (): JSX.Element => {
  const [appState, setAppState] = useState<AppState>({
    loading: false,
    error: undefined,
  });

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Global error handler
  const handleError = useCallback((error: string) => {
    setAppState(prev => ({ ...prev, error }));
    setSnackbar({
      open: true,
      message: error,
      severity: 'error',
    });
  }, []);

  // Global success handler
  const handleSuccess = useCallback((message: string) => {
    setSnackbar({
      open: true,
      message,
      severity: 'success',
    });
  }, []);

  // Close snackbar
  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Update app state
  const updateAppState = useCallback((updates: Partial<AppState>) => {
    setAppState(prev => ({ ...prev, ...updates }));
  }, []);

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ backgroundColor: '#0078d4' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Microsoft Certification Practice Assessment
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            AI Voice Assistant
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 3, mb: 3 }}>
        <Routes>
          <Route
            path="/"
            element={
              <HomePage
                appState={appState}
                updateAppState={updateAppState}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            }
          />
          <Route
            path="/assessment/:certificationCode"
            element={
              <AssessmentPage
                appState={appState}
                updateAppState={updateAppState}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            }
          />
          <Route
            path="/summary/:sessionId"
            element={
              <SummaryPage
                appState={appState}
                updateAppState={updateAppState}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>

      {/* Global Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;