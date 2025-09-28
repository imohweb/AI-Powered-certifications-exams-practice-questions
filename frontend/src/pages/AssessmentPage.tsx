import React from 'react';
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Button,
  LinearProgress,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  IconButton,
  Switch,
  FormGroup,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  InputLabel,
} from '@mui/material';
import {
  VolumeUp,
  CheckCircle,
  Cancel,
  Mic,
  MicOff,
  NavigateBefore,
  NavigateNext,
  Quiz,
  Stop,
  Home,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { AppState, PracticeAssessment, QuestionType } from '../types';
import { assessmentApi, audioApi, handleApiError } from '../services/api';

interface QuestionState {
  selectedAnswers: string[];
  isAnswered: boolean;
  isChecked: boolean;
  showResults: boolean;
  isCorrect?: boolean;
}

const AssessmentPage = ({
  appState: { audioEnabled = true },
  updateAppState,
  onError,
  onSuccess
}: {
  appState: AppState;
  updateAppState: (updates: Partial<AppState>) => void;
  onError: (message: string) => void;
  onSuccess: (message: string) => void;
}) => {
  const { certificationCode } = useParams<{ certificationCode: string }>();
  const navigate = useNavigate();
  
  // Core State
  const [assessment, setAssessment] = useState<PracticeAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questionStates, setQuestionStates] = useState<Map<number, QuestionState>>(new Map());
  
  // Voice State
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isReading, setIsReading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en'); // Language selection
  
  // Refs
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);
  const recognitionRef = useRef<any>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Initialize speech synthesis
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
    }
  }, []);

  // Initialize speech recognition with enhanced debugging and auto-restart
  useEffect(() => {
    if (typeof window !== 'undefined' && voiceEnabled) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        console.log('🎤 Initializing Speech Recognition...');
        const recognition = new SpeechRecognition();
        
        // Enhanced configuration
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 5;
        
        recognition.onstart = () => {
          console.log('🎤 Speech recognition started - Say "option 1", "option 2", etc.');
          setIsListening(true);
        };
        
        recognition.onresult = (event: any) => {
          console.log('🎤 Speech recognition result event received');
          const result = event.results[event.results.length - 1];
          const transcript = result[0].transcript;
          const confidence = result[0].confidence;
          
          console.log('🎤 Primary transcript:', transcript);
          console.log('🎤 Confidence:', confidence);
          
          // Show alternatives for debugging
          if (result.alternatives && result.alternatives.length > 1) {
            console.log('🎤 Alternative transcripts:');
            for (let i = 0; i < Math.min(result.alternatives.length, 3); i++) {
              console.log(`  ${i + 1}: "${result.alternatives[i].transcript}" (${result.alternatives[i].confidence})`);
            }
          }
          
          // Handle voice command directly here to avoid dependency issues
          if (transcript && transcript.trim()) {
            console.log('🎤 Processing transcript:', transcript);
            // We'll trigger a custom event that the handleVoiceCommand can listen to
            window.dispatchEvent(new CustomEvent('voiceCommand', { detail: transcript }));
          }
        };
        
        recognition.onerror = (event: any) => {
          console.error('🎤 Speech recognition error:', event.error, event);
          setIsListening(false);
          
          switch (event.error) {
            case 'not-allowed':
              onError('🎤 Microphone access denied. Please allow microphone permissions and refresh.');
              break;
            case 'no-speech':
              console.log('🎤 No speech detected, will continue listening...');
              // Don't show error, just continue
              break;
            case 'audio-capture':
              onError('🎤 No microphone found. Please check your microphone connection.');
              break;
            case 'network':
              onError('🎤 Network error. Please check your internet connection.');
              break;
            case 'aborted':
              console.log('🎤 Speech recognition aborted');
              break;
            default:
              onError(`🎤 Speech recognition error: ${event.error}`);
          }
        };
        
        recognition.onend = () => {
          console.log('🎤 Speech recognition ended');
          setIsListening(false);
          
          // Auto-restart if still enabled and page is focused
          if (voiceEnabled && document.hasFocus()) {
            console.log('🎤 Auto-restarting speech recognition in 500ms...');
            setTimeout(() => {
              if (voiceEnabled && recognitionRef.current) {
                try {
                  recognitionRef.current.start();
                } catch (e) {
                  console.log('🎤 Could not restart:', e.message);
                }
              }
            }, 500);
          }
        };
        
        recognition.onnomatch = () => {
          console.log('🎤 No match found - speech was unclear');
          onError('Could not understand the command clearly. Please speak clearly and try again.');
        };
        
        recognition.onspeechstart = () => {
          console.log('🎤 Speech detected - processing...');
        };
        
        recognition.onspeechend = () => {
          console.log('🎤 Speech ended - analyzing...');
        };
        
        recognitionRef.current = recognition;
        console.log('🎤 Speech Recognition setup complete');
      } else {
        console.warn('🎤 Speech recognition not supported');
        onError('Voice recognition requires Chrome, Edge, or Safari browser with microphone permissions.');
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        console.log('🎤 Cleaning up Speech Recognition');
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.error('🎤 Error stopping recognition:', error);
        }
      }
    };
  }, [voiceEnabled, onError]);

  // Load assessment
  useEffect(() => {
    const loadAssessment = async () => {
      if (!certificationCode) return;
      
      try {
        setLoading(true);
        console.log(`🔄 Loading assessment for certification: ${certificationCode}`);
        
        // Retry mechanism for first-time loading
        let assessmentData: PracticeAssessment | null = null;
        let lastError: any = null;
        
        for (let attempt = 1; attempt <= 3; attempt++) {
          try {
            console.log(`📝 Attempt ${attempt} to load ${certificationCode}...`);
            assessmentData = await assessmentApi.getAssessment(certificationCode);
            console.log(`✅ Assessment loaded on attempt ${attempt}`);
            break;
          } catch (error) {
            lastError = error;
            console.log(`⚠️ Attempt ${attempt} failed, retrying...`);
            
            if (attempt < 3) {
              // Wait before retry (exponential backoff)
              await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            }
          }
        }
        
        if (!assessmentData) {
          throw lastError || new Error('Failed to load assessment after multiple attempts');
        }
        
        console.log(`✅ Assessment loaded successfully:`, {
          id: assessmentData.id,
          certification_code: assessmentData.certification_code,
          title: assessmentData.title,
          totalQuestions: assessmentData.questions.length
        });
        
        setAssessment(assessmentData);
        
        // Initialize question states
        const initialStates = new Map<number, QuestionState>();
        assessmentData.questions.forEach((_, index) => {
          initialStates.set(index, {
            selectedAnswers: [],
            isAnswered: false,
            isChecked: false,
            showResults: false,
          });
        });
        setQuestionStates(initialStates);
        
        onSuccess(`Loaded ${assessmentData.questions.length} questions for ${certificationCode}`);
      } catch (error) {
        console.error(`❌ Failed to load assessment for ${certificationCode}:`, error);
        const errorMessage = handleApiError(error);
        onError(`Failed to load assessment: ${errorMessage}`);
      } finally {
        setLoading(false);
      }
    };

    loadAssessment();
  }, [certificationCode, onError, onSuccess]);

  // Load multilingual voices
  useEffect(() => {
    const loadMultilingualVoices = async () => {
      try {
        console.log('🌐 Loading multilingual voices...');
        const voices = await audioApi.getMultilingualVoices();
        console.log('✅ Multilingual voices loaded:', voices);
      } catch (error) {
        console.error('❌ Failed to load multilingual voices:', error);
      }
    };

    loadMultilingualVoices();
  }, []);

  // Get current question state
  const getCurrentQuestionState = useCallback((): QuestionState => {
    return questionStates.get(currentQuestionIndex) || {
      selectedAnswers: [],
      isAnswered: false,
      isChecked: false,
      showResults: false
    };
  }, [questionStates, currentQuestionIndex]);

  // Update question state
  const updateQuestionState = useCallback((updates: Partial<QuestionState>) => {
    const currentState = getCurrentQuestionState();
    const newState = { ...currentState, ...updates };
    setQuestionStates(prev => new Map(prev.set(currentQuestionIndex, newState)));
  }, [getCurrentQuestionState, currentQuestionIndex]);

  // Handle answer selection
  const handleAnswerSelect = useCallback((answerId: string) => {
    const currentQuestion = assessment?.questions[currentQuestionIndex];
    if (!currentQuestion) return;

    const currentState = getCurrentQuestionState();
    let newSelectedAnswers: string[];

    if (currentQuestion.question_type === QuestionType.MULTIPLE_CHOICE) {
      // Single selection for multiple choice
      newSelectedAnswers = [answerId];
    } else {
      // Multiple selection for other types
      newSelectedAnswers = currentState.selectedAnswers.includes(answerId) 
        ? currentState.selectedAnswers.filter(id => id !== answerId)
        : [...currentState.selectedAnswers, answerId];
    }

    updateQuestionState({
      selectedAnswers: newSelectedAnswers,
      isAnswered: newSelectedAnswers.length > 0,
      showResults: false,
      isChecked: false
    });
  }, [assessment, currentQuestionIndex, getCurrentQuestionState, updateQuestionState]);

  // Fallback to browser speech synthesis
  const fallbackToLocalSpeech = useCallback((textToRead: string) => {
    console.log('🔊 Using browser speech synthesis as fallback');
    
    if (!speechSynthesisRef.current) return;
    
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.rate = 0.75;
    utterance.volume = 0.8;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';
    
    // Try to use a female voice if available
    const voices = speechSynthesisRef.current.getVoices();
    const femaleVoice = voices.find(voice => 
      voice.name.toLowerCase().includes('female') || 
      voice.name.toLowerCase().includes('jenny') ||
      voice.name.toLowerCase().includes('sarah') ||
      voice.name.toLowerCase().includes('samantha')
    );
    if (femaleVoice) {
      utterance.voice = femaleVoice;
      console.log('🔊 Using voice:', femaleVoice.name);
    }
    
    utterance.onstart = () => setIsReading(true);
    utterance.onend = () => setIsReading(false);
    utterance.onerror = () => setIsReading(false);
    
    currentUtteranceRef.current = utterance;
    speechSynthesisRef.current.speak(utterance);
  }, []);

  // Enhanced multilingual speech using Azure Speech Service
  const readQuestionWithAzureSpeech = useCallback(async (languageCode: string = selectedLanguage) => {
    if (!voiceEnabled || !assessment) return;

    try {
      console.log(`🌐 Reading question using Azure Speech Service in ${languageCode}`);
      setIsReading(true);

      const currentQuestion = assessment.questions[currentQuestionIndex];
      if (!currentQuestion) return;

      // Extract answer texts
      const answerTexts = currentQuestion.answers.map(answer => answer.text);

      // Generate multilingual question audio
      const audioResponse = await audioApi.generateMultilingualQuestionAudio(
        currentQuestion.text,
        answerTexts,
        languageCode
      );

      if (audioResponse?.audio_url) {
        // Play the generated audio
        const audio = new Audio(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}${audioResponse.audio_url}`);
        
        audio.onended = () => {
          setIsReading(false);
          console.log('🔊 Azure Speech playback completed');
        };
        
        audio.onerror = () => {
          console.error('🔊 Azure Speech playback failed, falling back to browser speech');
          setIsReading(false);
          fallbackToLocalSpeech(currentQuestion.text);
        };

        await audio.play();
        console.log(`✅ Playing Azure Speech audio in ${languageCode}`);
      } else {
        throw new Error('No audio URL received');
      }

    } catch (error) {
      console.error('🔊 Azure Speech failed, falling back to browser speech:', error);
      setIsReading(false);
      
      // Fallback to browser speech
      const currentQuestion = assessment.questions[currentQuestionIndex];
      if (currentQuestion) {
        fallbackToLocalSpeech(currentQuestion.text);
      }
    }
  }, [voiceEnabled, assessment, currentQuestionIndex, selectedLanguage, fallbackToLocalSpeech]);

  // Enhanced feedback speech using secondary voice
  const readFeedbackWithAzureSpeech = useCallback(async (
    feedbackText: string, 
    isCorrect: boolean = true, 
    languageCode: string = selectedLanguage
  ) => {
    if (!voiceEnabled) return;

    try {
      console.log(`🔊 Reading feedback with Azure Speech (${isCorrect ? 'correct' : 'incorrect'}) in ${languageCode}`);

      // Generate feedback audio with secondary voice
      const audioResponse = await audioApi.generateFeedbackAudio(
        feedbackText,
        isCorrect,
        languageCode
      );

      if (audioResponse?.audio_url) {
        // Play the generated audio
        const audio = new Audio(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}${audioResponse.audio_url}`);
        
        audio.onended = () => {
          console.log('🔊 Azure feedback speech completed');
        };
        
        audio.onerror = () => {
          console.error('🔊 Azure feedback speech failed, falling back to browser speech');
          fallbackToLocalSpeech(feedbackText);
        };

        await audio.play();
        console.log(`✅ Playing Azure feedback audio in ${languageCode}`);
      } else {
        throw new Error('No audio URL received');
      }

    } catch (error) {
      console.error('🔊 Azure feedback speech failed, falling back to browser speech:', error);
      fallbackToLocalSpeech(feedbackText);
    }
  }, [voiceEnabled, selectedLanguage, fallbackToLocalSpeech]);

  // Read question aloud using Azure Speech Service with multilingual support
  const readQuestion = useCallback(async () => {
    // Use the multilingual version with the selected language
    await readQuestionWithAzureSpeech(selectedLanguage);
  }, [readQuestionWithAzureSpeech, selectedLanguage]);

  // Stop reading
  const stopReading = useCallback(() => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsReading(false);
    }
  }, []);

  // Check answer - simple wrapper function
  const checkAnswer = useCallback(async () => {
    const currentQuestion = assessment?.questions[currentQuestionIndex];
    const currentState = getCurrentQuestionState();
    
    if (!currentQuestion || !currentState.isAnswered) {
      onError('Please select an answer first');
      return;
    }
    
    // Check if the selected answers are correct
    const selectedSet = new Set(currentState.selectedAnswers);
    const correctSet = new Set(currentQuestion.correct_answer_ids);
    const isCorrect = selectedSet.size === correctSet.size && 
                     Array.from(selectedSet).every(id => correctSet.has(id));
    
    updateQuestionState({
      isChecked: true,
      showResults: true,
      isCorrect
    });
    
    // Provide voice feedback using Azure Speech Service with secondary voice
    if (voiceEnabled) {
      const feedbackText = isCorrect 
        ? 'Correct! Well done. Say "next question" to continue.' 
        : 'Incorrect. Please review the explanation. Say "next question" to continue.';
      
      await readFeedbackWithAzureSpeech(feedbackText, isCorrect, selectedLanguage);
    }
    
    const message = isCorrect ? 'Correct answer!' : 'Incorrect answer. Please review the explanation.';
    if (isCorrect) {
      onSuccess(message);
    } else {
      onError(message);
    }
  }, [assessment, currentQuestionIndex, getCurrentQuestionState, updateQuestionState, voiceEnabled, onSuccess, onError, readFeedbackWithAzureSpeech, selectedLanguage]);

  // Handle voice commands
  const handleVoiceCommand = useCallback(async (transcript: string) => {
    if (!assessment) return;
    
    console.log('Voice command received:', transcript);

    // Stop reading if user interrupts
    if (isReading) {
      stopReading();
    }
    
    // Normalize transcript for better matching
    const normalizedTranscript = transcript.toLowerCase().trim();
    
    // Check for "next question" command
    if (normalizedTranscript.includes('next question') || 
        (normalizedTranscript.includes('next') && normalizedTranscript.includes('question'))) {
      const currentState = getCurrentQuestionState();
      
      if (!currentState.isAnswered) {
        onError('Please select an answer before moving to the next question');
        return;
      }
      
      if (!currentState.isChecked) {
        onError('Please check your answer before moving to the next question');
        return;
      }
      
      if (currentQuestionIndex < assessment.questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        onSuccess('Moving to next question');
        
        // Automatically start reading the new question if voice is enabled
        if (voiceEnabled) {
          // Small delay to ensure the component has updated
          setTimeout(async () => {
            await readQuestionWithAzureSpeech(selectedLanguage);
          }, 500);
        }
      } else {
        onSuccess('You have completed all questions!');
      }
      return;
    }

    // Check for "previous question" command
    if (normalizedTranscript.includes('previous question') || 
        (normalizedTranscript.includes('previous') && normalizedTranscript.includes('question'))) {
      if (currentQuestionIndex > 0) {
        setCurrentQuestionIndex(prev => prev - 1);
        onSuccess('Moving to previous question');
      } else {
        onSuccess('You are on the first question!');
      }
      return;
    }

    // Check for "check answer" command
    if (normalizedTranscript.includes('check answer') || 
        normalizedTranscript.includes('check my answer') ||
        normalizedTranscript.includes('verify answer')) {
      const currentQuestion = assessment?.questions[currentQuestionIndex];
      const currentState = getCurrentQuestionState();
      
      if (!currentQuestion || !currentState.isAnswered) {
        onError('Please select an answer first');
        return;
      }
      
      // Check if the selected answers are correct
      const selectedSet = new Set(currentState.selectedAnswers);
      const correctSet = new Set(currentQuestion.correct_answer_ids);
      const isCorrect = selectedSet.size === correctSet.size && 
                       Array.from(selectedSet).every(id => correctSet.has(id));
      
      updateQuestionState({
        isChecked: true,
        showResults: true,
        isCorrect
      });
      
      // Provide voice feedback using Azure Speech Service with secondary voice
      if (voiceEnabled) {
        const feedbackText = isCorrect 
          ? 'Correct! Well done. Say "next question" to continue.' 
          : 'Incorrect. Please review the explanation. Say "next question" to continue.';
        
        await readFeedbackWithAzureSpeech(feedbackText, isCorrect, selectedLanguage);
      }
      
      const message = isCorrect ? 'Correct answer!' : 'Incorrect answer. Please review the explanation.';
      if (isCorrect) {
        onSuccess(message);
      } else {
        onError(message);
      }
      return;
    }

    // Parse voice commands for options with multiple patterns
    const currentQuestion = assessment.questions[currentQuestionIndex];
    let optionNumber = -1;
    
    // Try different patterns to match options
    const patterns = [
      /(?:option|answer|choice)\s*(?:number\s*)?(\d+)/i,
      /(?:select|pick|choose)\s*(?:option|answer|choice)?\s*(?:number\s*)?(\d+)/i,
      /(?:number|#)\s*(\d+)/i,
      /^(\d+)$/i, // Just a number
    ];
    
    for (const pattern of patterns) {
      const match = normalizedTranscript.match(pattern);
      if (match) {
        optionNumber = parseInt(match[1]) - 1; // Convert to 0-based index
        console.log(`Matched option pattern: ${pattern}, option number: ${optionNumber + 1}`);
        break;
      }
    }
    
    // Also check for written numbers
    const writtenNumbers = {
      'one': 1, 'first': 1,
      'two': 2, 'second': 2,
      'three': 3, 'third': 3,
      'four': 4, 'fourth': 4,
      'five': 5, 'fifth': 5
    };
    
    if (optionNumber === -1) {
      for (const [word, number] of Object.entries(writtenNumbers)) {
        if (normalizedTranscript.includes(word)) {
          optionNumber = number - 1;
          console.log(`Matched written number: ${word}, option number: ${number}`);
          break;
        }
      }
    }
    
    if (optionNumber >= 0 && optionNumber < currentQuestion.answers.length) {
      const answerId = currentQuestion.answers[optionNumber].id;
      handleAnswerSelect(answerId);
      
      const selectedAnswer = currentQuestion.answers[optionNumber];
      const message = `Selected option ${optionNumber + 1}: ${selectedAnswer.text.substring(0, 50)}${selectedAnswer.text.length > 50 ? '...' : ''}`;
      onSuccess(message);
      
      // Provide voice feedback using Azure Speech Service with secondary voice
      if (voiceEnabled) {
        const feedbackText = `You selected option ${optionNumber + 1}. Say "check answer" to verify, or "next question" to continue.`;
        await readFeedbackWithAzureSpeech(feedbackText, true, selectedLanguage);
      }
      return;
    }
    
    // If we get here, the command wasn't recognized
    console.log(`Unrecognized voice command: "${transcript}"`);
    onError(`Voice command not recognized. Please say "option 1", "option 2", "option 3", "option 4", "check answer", or "next question"`);
  }, [assessment, currentQuestionIndex, isReading, stopReading, getCurrentQuestionState, handleAnswerSelect, updateQuestionState, voiceEnabled, onSuccess, onError, readFeedbackWithAzureSpeech, selectedLanguage, readQuestionWithAzureSpeech]);

  // Listen for voice command events
  useEffect(() => {
    const handleVoiceCommandEvent = (event: any) => {
      const transcript = event.detail;
      console.log('🎤 Received voice command event:', transcript);
      handleVoiceCommand(transcript);
    };

    window.addEventListener('voiceCommand', handleVoiceCommandEvent);
    
    return () => {
      window.removeEventListener('voiceCommand', handleVoiceCommandEvent);
    };
  }, [handleVoiceCommand]);

  // Start voice listening
  const startListening = useCallback(() => {
    if (!voiceEnabled || !recognitionRef.current || isListening) return;
    
    try {
      console.log('🎤 Starting voice recognition...');
      recognitionRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('🎤 Failed to start voice recognition:', error);
      onError('Failed to start voice recognition. Please check microphone permissions.');
    }
  }, [voiceEnabled, isListening, onError]);

  // Stop voice listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (error) {
        console.error('Failed to stop voice recognition:', error);
      }
    }
  }, [isListening]);

  // Navigation handlers
  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const goToNextQuestion = async () => {
    const currentState = getCurrentQuestionState();
    
    if (!currentState.isAnswered) {
      onError('Please select an answer before moving to the next question');
      return;
    }
    
    if (!currentState.isChecked) {
      onError('Please check your answer before moving to the next question');
      return;
    }
    
    if (currentQuestionIndex < (assessment?.questions.length || 0) - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      
      // Automatically start reading the new question if voice is enabled
      if (voiceEnabled) {
        // Small delay to ensure the component has updated
        setTimeout(async () => {
          await readQuestionWithAzureSpeech(selectedLanguage);
        }, 500);
      }
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading assessment...</Typography>
      </Box>
    );
  }

  if (!assessment) {
    return (
      <Box sx={{ maxWidth: 800, mx: 'auto', py: 3 }}>
        <Alert severity="error">
          Assessment not found. Please check the certification code and try again.
        </Alert>
      </Box>
    );
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];
  const currentState = getCurrentQuestionState();

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 3 }}>
      {/* Header with Progress */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4">
            {assessment.title}
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Home />}
            onClick={() => navigate('/')}
            sx={{ ml: 2 }}
          >
            Return to Home
          </Button>
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Question {currentQuestionIndex + 1} of {assessment.questions.length}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={((currentQuestionIndex + 1) / assessment.questions.length) * 100} 
            sx={{ height: 8, borderRadius: 4 }} 
          />
        </Box>

        {/* Voice Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={voiceEnabled}
                onChange={(e) => setVoiceEnabled(e.target.checked)}
              />
            }
            label="Voice Features"
          />
          
          {voiceEnabled && (
            <>
              {/* Language selector for multilingual voice */}
              <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
                <InputLabel id="language-select-label">Voice Language</InputLabel>
                <Select
                  labelId="language-select-label"
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  label="Voice Language"
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                  <MenuItem value="it">Italian</MenuItem>
                  <MenuItem value="pt">Portuguese</MenuItem>
                  <MenuItem value="ja">Japanese</MenuItem>
                  <MenuItem value="ko">Korean</MenuItem>
                  <MenuItem value="zh">Chinese</MenuItem>
                  <MenuItem value="ar">Arabic</MenuItem>
                  <MenuItem value="hi">Hindi</MenuItem>
                  <MenuItem value="ru">Russian</MenuItem>
                </Select>
              </FormControl>

              <Button
                variant="contained"
                size="small"
                startIcon={isReading ? <Stop /> : <VolumeUp />}
                onClick={isReading ? stopReading : readQuestion}
                color={isReading ? 'error' : 'primary'}
              >
                {isReading ? 'Stop Reading' : 'Read Question'}
              </Button>
              
              <IconButton
                onClick={isListening ? stopListening : startListening}
                color={isListening ? 'error' : 'primary'}
                size="small"
              >
                {isListening ? <MicOff /> : <Mic />}
              </IconButton>
            </>
          )}
        </Box>

        {/* Status Alerts */}
        {isReading && (
          <Alert severity="info" sx={{ mb: 1 }}>
            🔊 Reading question aloud... You can interrupt by saying a command or clicking "Stop Reading"
          </Alert>
        )}
        
        {isListening && voiceEnabled && (
          <Alert severity="success" sx={{ mb: 1 }}>
            🎤 Listening for voice commands... Say "option 1-4", "check answer", or "next question"
          </Alert>
        )}
      </Paper>

      {/* Current Question */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" component="div" sx={{ mb: 3, lineHeight: 1.6 }}>
            {currentQuestion.text}
          </Typography>

          {/* Answer Options */}
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Select your answer:
            </FormLabel>
            
            {currentQuestion.question_type === QuestionType.MULTIPLE_CHOICE ? (
              <RadioGroup
                value={currentState.selectedAnswers[0] || ''}
                onChange={(e) => handleAnswerSelect(e.target.value)}
              >
                {currentQuestion.answers.map((answer, index) => (
                  <FormControlLabel
                    key={answer.id}
                    value={answer.id}
                    control={<Radio />}
                    label={
                      <Box>
                        <Typography component="span" sx={{ fontWeight: 'medium' }}>
                          Option {index + 1}:
                        </Typography>
                        <Typography component="span" sx={{ ml: 1 }}>
                          {answer.text}
                        </Typography>
                      </Box>
                    }
                    sx={{ 
                      mb: 1, 
                      p: 1.5, 
                      ml: 0, 
                      mr: 0, 
                      border: '1px solid',
                      borderColor: 'grey.300',
                      borderRadius: 1,
                      '&:hover': { bgcolor: 'grey.50' },
                      ...(currentState.selectedAnswers.includes(answer.id) && { 
                        bgcolor: 'primary.50',
                        borderColor: 'primary.main'
                      })
                    }}
                  />
                ))}
              </RadioGroup>
            ) : (
              <FormGroup>
                {currentQuestion.answers.map((answer, index) => (
                  <FormControlLabel
                    key={answer.id}
                    control={
                      <Checkbox
                        checked={currentState.selectedAnswers.includes(answer.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            handleAnswerSelect(answer.id);
                          } else {
                            handleAnswerSelect(answer.id); // This will toggle it off
                          }
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography component="span" sx={{ fontWeight: 'medium' }}>
                          Option {index + 1}:
                        </Typography>
                        <Typography component="span" sx={{ ml: 1 }}>
                          {answer.text}
                        </Typography>
                      </Box>
                    }
                    sx={{ 
                      mb: 1, 
                      p: 1.5, 
                      ml: 0, 
                      mr: 0, 
                      border: '1px solid',
                      borderColor: 'grey.300',
                      borderRadius: 1,
                      '&:hover': { bgcolor: 'grey.50' },
                      ...(currentState.selectedAnswers.includes(answer.id) && { 
                        bgcolor: 'primary.50',
                        borderColor: 'primary.main'
                      })
                    }}
                  />
                ))}
              </FormGroup>
            )}
          </FormControl>

          {/* Answer Results */}
          {currentState.showResults && (
            <Box sx={{ mt: 3 }}>
              <Alert 
                severity={currentState.isCorrect ? 'success' : 'error'}
                sx={{ mb: 2 }}
                icon={currentState.isCorrect ? <CheckCircle /> : <Cancel />}
              >
                <Typography variant="h6" component="div">
                  {currentState.isCorrect ? 'Correct!' : 'Incorrect'}
                </Typography>
                <Typography variant="body2">
                  {currentState.isCorrect 
                    ? 'Well done! You selected the right answer.' 
                    : 'The correct answer(s) are highlighted below.'}
                </Typography>
              </Alert>

              {/* Show correct answers */}
              <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                Correct Answer(s):
              </Typography>
              {currentQuestion.answers
                .filter(answer => currentQuestion.correct_answer_ids.includes(answer.id))
                .map((answer) => (
                  <Chip
                    key={answer.id}
                    label={`${currentQuestion.answers.indexOf(answer) + 1}. ${answer.text}`}
                    color="success"
                    sx={{ m: 0.5, height: 'auto', '& .MuiChip-label': { whiteSpace: 'normal' } }}
                  />
                ))}

              {/* Show explanation if available */}
              {currentQuestion.explanation && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
                    Explanation:
                  </Typography>
                  <Typography variant="body2" sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    {currentQuestion.explanation}
                  </Typography>
                </Box>
              )}
            </Box>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              startIcon={<NavigateBefore />}
              disabled={currentQuestionIndex === 0}
              onClick={goToPreviousQuestion}
            >
              Previous
            </Button>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              {currentState.isAnswered && !currentState.isChecked && (
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<Quiz />}
                  onClick={checkAnswer}
                >
                  Check Answer
                </Button>
              )}
              
              <Button
                variant="contained"
                endIcon={<NavigateNext />}
                disabled={
                  currentQuestionIndex === assessment.questions.length - 1 ||
                  !currentState.isAnswered ||
                  !currentState.isChecked
                }
                onClick={goToNextQuestion}
                color="primary"
              >
                Next Question
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Voice Instructions */}
      {voiceEnabled && (
        <Paper sx={{ p: 2, bgcolor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'info.main' }}>
            🎤 Voice Commands Available:
          </Typography>
          <Box sx={{ '& > *': { mb: 0.5 } }}>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Read question"</Box> - AI will read the current question and all answer options aloud
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Option 1", "Option 2", "Option 3", "Option 4"</Box> - Select answer options by voice
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Number 1", "Choice 2", "Answer 3"</Box> - Alternative ways to select options
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Check answer"</Box> - Verify if your selected answer is correct
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Next question"</Box> - Move to the next question (after checking answer)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Previous question"</Box> - Go back to the previous question
            </Typography>
            <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', color: 'info.dark' }}>
              💡 Tip: Click the microphone icon to start listening, then speak your command clearly.
            </Typography>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default AssessmentPage;
