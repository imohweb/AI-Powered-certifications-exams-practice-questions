/**
 * API service for communicating with the FastAPI backend.
 * Handles all HTTP requests and response processing.
 */

import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  PracticeAssessment,
  CertificationInfo,
  UserSession,
  Question,
  SessionProgress,
  AnswerSubmissionResult,
  SessionSummary,
  AudioRequest,
  AudioResponse,
  VoicesResponse,
  ApiError,
  UserAnswer
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response Success: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: error.message,
      status: error.response?.status,
      code: error.code,
    };

    if (error.response?.data) {
      const data = error.response.data as any;
      apiError.message = data.detail || data.message || error.message;
    }

    console.error('API Response Error Details:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: apiError.message,
      code: error.code,
      responseData: error.response?.data
    });
    return Promise.reject(apiError);
  }
);

/**
 * Assessment API endpoints
 */
export const assessmentApi = {
  /**
   * Get list of available certifications
   */
  getCertifications: async (): Promise<CertificationInfo[]> => {
    const response = await api.get<CertificationInfo[]>('/assessments/certifications');
    return response.data;
  },

  /**
   * Get practice assessment for a specific certification
   */
  getAssessment: async (certificationCode: string): Promise<PracticeAssessment> => {
    const response = await api.get<PracticeAssessment>(`/assessments/${certificationCode}`);
    return response.data;
  },

  /**
   * Get sample assessment for testing
   */
  getSampleAssessment: async (certificationCode: string): Promise<PracticeAssessment> => {
    const response = await api.get<PracticeAssessment>(`/assessments/${certificationCode}/sample`);
    return response.data;
  },

  /**
   * Trigger background scraping of assessment
   */
  scrapeAssessment: async (certificationCode: string): Promise<any> => {
    const response = await api.post(`/assessments/${certificationCode}/scrape`);
    return response.data;
  },

  /**
   * Get scraping status
   */
  getScrapingStatus: async (certificationCode: string): Promise<any> => {
    const response = await api.get(`/assessments/${certificationCode}/scrape/status`);
    return response.data;
  },

  /**
   * Clear assessment cache
   */
  clearCache: async (certificationCode: string): Promise<any> => {
    const response = await api.delete(`/assessments/${certificationCode}/cache`);
    return response.data;
  },
};

/**
 * Session API endpoints
 */
export const sessionApi = {
  /**
   * Start a new practice session
   */
  startSession: async (
    certificationCode: string,
    autoProgression: boolean = true
  ): Promise<UserSession> => {
    const response = await api.post<UserSession>('/sessions/start', null, {
      params: {
        certification_code: certificationCode,
        auto_progression: autoProgression,
      },
    });
    return response.data;
  },

  /**
   * Get current question for a session
   */
  getCurrentQuestion: async (sessionId: string): Promise<Question> => {
    const response = await api.get<Question>(`/sessions/${sessionId}/current-question`);
    return response.data;
  },

  /**
   * Submit an answer for the current question
   */
  submitAnswer: async (
    sessionId: string,
    questionId: string,
    selectedAnswerIds: string[],
    timeSpentSeconds?: number
  ): Promise<AnswerSubmissionResult> => {
    const response = await api.post<AnswerSubmissionResult>(
      `/sessions/${sessionId}/submit-answer`,
      null,
      {
        params: {
          question_id: questionId,
          selected_answer_ids: selectedAnswerIds,
          time_spent_seconds: timeSpentSeconds,
        },
      }
    );
    return response.data;
  },

  /**
   * Advance to next question manually
   */
  nextQuestion: async (sessionId: string): Promise<Question | null> => {
    const response = await api.post(`/sessions/${sessionId}/next-question`);
    return response.data;
  },

  /**
   * Get session progress
   */
  getProgress: async (sessionId: string): Promise<SessionProgress> => {
    const response = await api.get<SessionProgress>(`/sessions/${sessionId}/progress`);
    return response.data;
  },

  /**
   * Get session summary
   */
  getSummary: async (sessionId: string): Promise<SessionSummary> => {
    const response = await api.get<SessionSummary>(`/sessions/${sessionId}/summary`);
    return response.data;
  },

  /**
   * Get all answers for a session
   */
  getAnswers: async (sessionId: string): Promise<UserAnswer[]> => {
    const response = await api.get<UserAnswer[]>(`/sessions/${sessionId}/answers`);
    return response.data;
  },

  /**
   * Update session settings
   */
  updateSettings: async (
    sessionId: string,
    settings: { auto_progression?: boolean }
  ): Promise<any> => {
    const response = await api.put(`/sessions/${sessionId}/settings`, null, {
      params: settings,
    });
    return response.data;
  },

  /**
   * End a session
   */
  endSession: async (sessionId: string): Promise<any> => {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  /**
   * Get active sessions
   */
  getActiveSessions: async (): Promise<any> => {
    const response = await api.get('/sessions/active');
    return response.data;
  },
};

/**
 * Audio API endpoints
 */
export const audioApi = {
  /**
   * Generate audio from text
   */
  generateAudio: async (request: AudioRequest): Promise<AudioResponse> => {
    const response = await api.post<AudioResponse>('/audio/generate', request);
    return response.data;
  },

  /**
   * Generate audio for a complete question
   */
  generateQuestionAudio: async (
    questionText: string,
    answers: string[],
    explanation?: string,
    voiceName?: string
  ): Promise<AudioResponse> => {
    const response = await api.post<AudioResponse>('/audio/generate/question', null, {
      params: {
        question_text: questionText,
        answers: answers,
        explanation: explanation,
        voice_name: voiceName,
      },
    });
    return response.data;
  },

  /**
   * Get available voices
   */
  getVoices: async (): Promise<VoicesResponse> => {
    const response = await api.get<VoicesResponse>('/audio/voices');
    return response.data;
  },

  /**
   * Test speech service
   */
  testService: async (): Promise<any> => {
    const response = await api.get('/audio/test');
    return response.data;
  },

  /**
   * Stream audio generation
   */
  streamAudio: async (request: AudioRequest): Promise<Blob> => {
    const response = await api.post('/audio/stream', request, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Clear audio cache
   */
  clearCache: async (): Promise<any> => {
    const response = await api.delete('/audio/cache');
    return response.data;
  },

  /**
   * Get cache statistics
   */
  getCacheStats: async (): Promise<any> => {
    const response = await api.get('/audio/cache/stats');
    return response.data;
  },

  /**
   * Generate multilingual audio
   */
  generateMultilingualAudio: async (
    text: string,
    languageCode: string = 'en',
    voiceType: string = 'primary'
  ): Promise<AudioResponse> => {
    const response = await api.post<AudioResponse>('/audio/generate/multilingual', null, {
      params: {
        text,
        language_code: languageCode,
        voice_type: voiceType
      }
    });
    return response.data;
  },

  /**
   * Generate multilingual question audio
   */
  generateMultilingualQuestionAudio: async (
    questionText: string,
    answers: string[],
    languageCode: string = 'en'
  ): Promise<AudioResponse> => {
    const response = await api.post<AudioResponse>('/audio/generate/question/multilingual', null, {
      params: {
        question_text: questionText,
        answers: answers.join(','),
        language_code: languageCode
      }
    });
    return response.data;
  },

  /**
   * Generate feedback audio with secondary voice
   */
  generateFeedbackAudio: async (
    feedbackText: string,
    isCorrect: boolean = true,
    languageCode: string = 'en',
    skipPrefix: boolean = false
  ): Promise<AudioResponse> => {
    const response = await api.post<AudioResponse>('/audio/generate/feedback', null, {
      params: {
        feedback_text: feedbackText,
        is_correct: isCorrect,
        language_code: languageCode,
        skip_prefix: skipPrefix
      }
    });
    return response.data;
  },

  /**
   * Get available multilingual voices
   */
  getMultilingualVoices: async (): Promise<any> => {
    const response = await api.get('/audio/voices/multilingual');
    return response.data;
  },
};

/**
 * Helper function to handle API errors consistently
 */
export const handleApiError = (error: any): string => {
  if (error.message) {
    return error.message;
  }
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  return 'An unexpected error occurred';
};

/**
 * Helper function to build audio URL
 */
export const buildAudioUrl = (audioPath: string): string => {
  // Use the same base URL as API calls, but remove /api/v1 suffix for audio files
  const apiBaseUrl = process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';
  const baseUrl = apiBaseUrl.replace('/api/v1', '');
  return `${baseUrl}${audioPath}`;
};

export default api;