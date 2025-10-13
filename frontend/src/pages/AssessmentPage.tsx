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
import { assessmentApi, audioApi, handleApiError, buildAudioUrl } from '../services/api';

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
  const [currentTranscript, setCurrentTranscript] = useState<string>(''); // Current speech transcript from microphone
  const [showTranscription, setShowTranscription] = useState(true); // Show real-time transcription display (enabled by default)
  
  // Progressive transcription state (for real-time text display)
  const [progressiveText, setProgressiveText] = useState<string>(''); // Text displayed progressively
  const [fullTranscriptionText, setFullTranscriptionText] = useState<string>(''); // Full text to display
  const progressiveTimerRef = useRef<NodeJS.Timeout | null>(null); // Timer for progressive display
  
  // Translation state (for displaying translated content in UI)
  const [translatedQuestions, setTranslatedQuestions] = useState<Map<number, string>>(new Map()); // Translated question text by index
  const [translatedAnswersMap, setTranslatedAnswersMap] = useState<Map<number, string[]>>(new Map()); // Translated answers by question index
  
  // Refs
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);
  const recognitionRef = useRef<any>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null); // Track current Azure audio

  // Initialize speech synthesis
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
    }
  }, []);

  // Initialize speech recognition with enhanced debugging and auto-restart
  useEffect(() => {
    if (typeof window !== 'undefined' && voiceEnabled) {
      // Clean up any existing recognition first
      if (recognitionRef.current) {
        console.log('🎤 Stopping existing speech recognition for language change');
        try {
          recognitionRef.current.stop();
          recognitionRef.current = null;
        } catch (error) {
          console.error('🎤 Error stopping existing recognition:', error);
        }
      }

      // Initialize new recognition
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        // Use the selected language for speech recognition
        const recognitionLang = getRecognitionLanguageCode(selectedLanguage);
          
        console.log(`🎤 Initializing Speech Recognition for ${recognitionLang} (${selectedLanguage.toUpperCase()})...`);
        const recognition = new SpeechRecognition();
        
        // Enhanced configuration
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = recognitionLang; // Use dynamic language
        recognition.maxAlternatives = 5;
        
        recognition.onstart = () => {
          const langName = selectedLanguage.toUpperCase();
          console.log(`🎤 Speech recognition started in ${langName} - Say "option 1", "option 2", etc.`);
          setIsListening(true);
          setCurrentTranscript(''); // Clear previous transcript
        };
        
        recognition.onresult = (event: any) => {
          console.log('🎤 Speech recognition result event received');
          const result = event.results[event.results.length - 1];
          const transcript = result[0].transcript;
          const confidence = result[0].confidence;
          
          console.log('🎤 Primary transcript:', transcript);
          console.log('🎤 Confidence:', confidence);
          
          // Update the transcript display
          setCurrentTranscript(transcript);
          
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
          setCurrentTranscript(''); // Clear transcript on error
          
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
  }, [voiceEnabled, selectedLanguage, onError]);

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

  // Cleanup audio on component unmount or navigation
  useEffect(() => {
    return () => {
      // Stop any playing audio
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
      
      // Stop browser speech synthesis
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel();
      }
      
      // Stop speech recognition
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          // Ignore errors if already stopped
        }
      }
      
      console.log('🧹 Audio cleanup completed on unmount');
    };
  }, []);

  // Language code mapping for speech recognition
  const getRecognitionLanguageCode = (languageCode: string): string => {
    const languageMap: { [key: string]: string } = {
      'en': 'en-US',
      'es': 'es-ES',
      'fr': 'fr-FR',
      'de': 'de-DE',
      'it': 'it-IT',
      'pt': 'pt-PT',
      'ja': 'ja-JP',
      'ko': 'ko-KR',
      'zh': 'zh-CN',
      'ar': 'ar-SA',
      'hi': 'hi-IN',
      'ru': 'ru-RU',
    };
    return languageMap[languageCode] || 'en-US';
  };

  // Multilingual voice command patterns
  const getVoiceCommandPatterns = (languageCode: string) => {
    const patterns: { [key: string]: any } = {
      'en': {
        stopReading: ['stop reading', 'stop', 'pause', 'quiet'],
        readQuestion: ['read question', 'read the question', 'read this question', 'repeat question', 'say question'],
        checkAnswer: ['check answer', 'check my answer', 'verify answer', 'submit answer'],
        nextQuestion: ['next question', 'next'],
        previousQuestion: ['previous question', 'previous'],
        optionPatterns: [
          /(?:option|answer|choice)\s*(?:number\s*)?([abcdef]|\d+)/i,
          /(?:select|pick|choose)\s*(?:option|answer|choice)?\s*(?:number\s*)?([abcdef]|\d+)/i,
          /(?:number|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /letter\s*([abcdef])/i
        ]
      },
      'es': {
        stopReading: ['parar', 'detener', 'pausa', 'silencio', 'para', 'stop'],
        readQuestion: ['leer pregunta', 'lee la pregunta', 'repetir pregunta', 'decir pregunta'],
        checkAnswer: ['verificar respuesta', 'comprobar respuesta', 'revisar respuesta'],
        nextQuestion: ['siguiente pregunta', 'siguiente', 'próxima pregunta'],
        previousQuestion: ['pregunta anterior', 'anterior', 'pregunta previa'],
        optionPatterns: [
          /(?:opción|respuesta|alternativa)\s*(?:número\s*)?([abcdef]|\d+)/i,
          /(?:seleccionar|elegir|escoger)\s*(?:opción|respuesta)?\s*(?:número\s*)?([abcdef]|\d+)/i,
          /(?:número|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /letra\s*([abcdef])/i
        ]
      },
      'fr': {
        stopReading: ['arrêter', 'stop', 'pause', 'silence', 'arrête'],
        readQuestion: ['lire question', 'lis la question', 'répéter question', 'dire question'],
        checkAnswer: ['vérifier réponse', 'contrôler réponse', 'valider réponse'],
        nextQuestion: ['question suivante', 'suivant', 'prochaine question'],
        previousQuestion: ['question précédente', 'précédent', 'question avant'],
        optionPatterns: [
          /(?:option|réponse|choix)\s*(?:numéro\s*)?([abcdef]|\d+)/i,
          /(?:sélectionner|choisir)\s*(?:option|réponse)?\s*(?:numéro\s*)?([abcdef]|\d+)/i,
          /(?:numéro|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /lettre\s*([abcdef])/i
        ]
      },
      'de': {
        stopReading: ['stoppen', 'anhalten', 'pause', 'ruhe', 'stop'],
        readQuestion: ['frage lesen', 'lies die frage', 'frage wiederholen', 'frage sagen'],
        checkAnswer: ['antwort prüfen', 'antwort überprüfen', 'antwort kontrollieren'],
        nextQuestion: ['nächste frage', 'weiter', 'nächste'],
        previousQuestion: ['vorherige frage', 'zurück', 'vorherige'],
        optionPatterns: [
          /(?:option|antwort|auswahl)\s*(?:nummer\s*)?([abcdef]|\d+)/i,
          /(?:wählen|auswählen)\s*(?:option|antwort)?\s*(?:nummer\s*)?([abcdef]|\d+)/i,
          /(?:nummer|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /buchstabe\s*([abcdef])/i
        ]
      },
      'it': {
        stopReading: ['fermare', 'stop', 'pausa', 'silenzio', 'basta'],
        readQuestion: ['leggi domanda', 'leggere la domanda', 'ripetere domanda', 'dire domanda'],
        checkAnswer: ['controllare risposta', 'verificare risposta', 'validare risposta'],
        nextQuestion: ['prossima domanda', 'avanti', 'domanda successiva'],
        previousQuestion: ['domanda precedente', 'indietro', 'domanda prima'],
        optionPatterns: [
          /(?:opzione|risposta|scelta)\s*(?:numero\s*)?([abcdef]|\d+)/i,
          /(?:selezionare|scegliere)\s*(?:opzione|risposta)?\s*(?:numero\s*)?([abcdef]|\d+)/i,
          /(?:numero|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /lettera\s*([abcdef])/i
        ]
      },
      'pt': {
        stopReading: ['parar', 'stop', 'pausa', 'silêncio', 'para'],
        readQuestion: ['ler pergunta', 'leia a pergunta', 'repetir pergunta', 'dizer pergunta'],
        checkAnswer: ['verificar resposta', 'conferir resposta', 'validar resposta'],
        nextQuestion: ['próxima pergunta', 'próximo', 'pergunta seguinte'],
        previousQuestion: ['pergunta anterior', 'anterior', 'pergunta prévia'],
        optionPatterns: [
          /(?:opção|resposta|alternativa)\s*(?:número\s*)?([abcdef]|\d+)/i,
          /(?:selecionar|escolher)\s*(?:opção|resposta)?\s*(?:número\s*)?([abcdef]|\d+)/i,
          /(?:número|#)\s*(\d+)/i,
          /^([abcdef]|\d+)$/i,
          /letra\s*([abcdef])/i
        ]
      }
    };
    
    return patterns[languageCode] || patterns['en']; // Default to English if language not supported
  };

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

    // Return the selected answer index for voice feedback
    return currentQuestion.answers.findIndex(answer => answer.id === answerId);
  }, [assessment, currentQuestionIndex, getCurrentQuestionState, updateQuestionState]);

  // Fallback to browser speech synthesis
  const fallbackToLocalSpeech = useCallback((textToRead: string) => {
    console.log('🔊 Using browser speech synthesis as fallback');
    
    if (!speechSynthesisRef.current) return;
    
    // Stop any HTML5 audio first
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
    
    // Cancel any ongoing speech synthesis
    speechSynthesisRef.current.cancel();
    
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

  // Progressive text display function (word-by-word animation)
  const startProgressiveTextDisplay = useCallback((fullText: string, durationSeconds: number) => {
    // Don't display if transcription is disabled
    if (!showTranscription) {
      return;
    }
    
    // Clear any existing progressive display
    if (progressiveTimerRef.current) {
      clearInterval(progressiveTimerRef.current);
      progressiveTimerRef.current = null;
    }
    
    setFullTranscriptionText(fullText);
    setProgressiveText('');
    
    // Split text into chunks (words + punctuation)
    // This regex keeps words together and splits on spaces
    const chunks: string[] = [];
    const regex = /\S+\s*/g; // Match non-whitespace followed by optional whitespace
    let match;
    
    while ((match = regex.exec(fullText)) !== null) {
      chunks.push(match[0]);
    }
    
    if (chunks.length === 0) {
      setProgressiveText(fullText);
      return;
    }
    
    // Calculate timing - aim for natural reading pace
    // Average reading speed is 2-3 words per second for TTS
    const totalChunks = chunks.length;
    const msPerChunk = Math.max(150, Math.min(600, (durationSeconds * 1000) / totalChunks));
    
    let currentIndex = 0;
    let displayedText = '';
    
    // Display chunks progressively
    progressiveTimerRef.current = setInterval(() => {
      if (currentIndex < chunks.length) {
        displayedText += chunks[currentIndex];
        setProgressiveText(displayedText);
        currentIndex++;
      } else {
        // All chunks displayed
        if (progressiveTimerRef.current) {
          clearInterval(progressiveTimerRef.current);
          progressiveTimerRef.current = null;
        }
      }
    }, msPerChunk);
    
  }, [showTranscription]);

  // Clear progressive text display
  const clearProgressiveTextDisplay = useCallback(() => {
    if (progressiveTimerRef.current) {
      clearInterval(progressiveTimerRef.current);
      progressiveTimerRef.current = null;
    }
    setProgressiveText('');
    setFullTranscriptionText('');
  }, []);

  // Enhanced multilingual speech using Azure Speech Service
  const readQuestionWithAzureSpeech = useCallback(async (languageCode: string = selectedLanguage, questionIndex?: number) => {
    if (!voiceEnabled || !assessment) return;

    try {
      // Use provided questionIndex or fallback to currentQuestionIndex
      const indexToRead = questionIndex !== undefined ? questionIndex : currentQuestionIndex;
      console.log(`🌐 Reading question ${indexToRead + 1} using Azure Speech Service in ${languageCode}`);
      setIsReading(true);

      const currentQuestion = assessment.questions[indexToRead];
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
        // Store translated content for UI display if available
        if (audioResponse.translated_question && audioResponse.translated_answers) {
          setTranslatedQuestions(prev => {
            const newMap = new Map(prev);
            newMap.set(indexToRead, audioResponse.translated_question!);
            return newMap;
          });
          setTranslatedAnswersMap(prev => {
            const newMap = new Map(prev);
            newMap.set(indexToRead, audioResponse.translated_answers!);
            return newMap;
          });
        }
        
        // Stop any currently playing audio first
        if (currentAudioRef.current) {
          currentAudioRef.current.pause();
          currentAudioRef.current = null;
        }
        
        // Stop browser speech synthesis
        if (speechSynthesisRef.current) {
          speechSynthesisRef.current.cancel();
        }

        // Clear any previous progressive text display BEFORE starting new one
        clearProgressiveTextDisplay();

        // Start progressive text display if we have translated text
        if (audioResponse.translated_text) {
          const duration = audioResponse.duration_seconds || 5; // Default to 5 seconds if not provided
          startProgressiveTextDisplay(audioResponse.translated_text, duration);
        }

        // Play the generated audio
        const audio = new Audio(buildAudioUrl(audioResponse.audio_url));
        currentAudioRef.current = audio; // Store reference for stopping
        
        audio.onended = () => {
          setIsReading(false);
          currentAudioRef.current = null;
          // Clear progressive text after a short delay
          setTimeout(() => clearProgressiveTextDisplay(), 2000);
          console.log('🔊 Azure Speech playback completed');
        };
        
        audio.onerror = () => {
          console.error('🔊 Azure Speech playback failed, falling back to browser speech');
          setIsReading(false);
          currentAudioRef.current = null;
          clearProgressiveTextDisplay();
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
      currentAudioRef.current = null;
      clearProgressiveTextDisplay();
      
      // Fallback to browser speech
      const currentQuestion = assessment.questions[currentQuestionIndex];
      if (currentQuestion) {
        fallbackToLocalSpeech(currentQuestion.text);
      }
    }
  }, [voiceEnabled, assessment, currentQuestionIndex, selectedLanguage, fallbackToLocalSpeech, startProgressiveTextDisplay, clearProgressiveTextDisplay]);

    // Enhanced feedback speech using secondary voice
  const readFeedbackWithAzureSpeech = useCallback(async (
    feedbackText: string, 
    isCorrect: boolean = true, 
    languageCode: string = selectedLanguage,
    pauseListeningFn?: () => void,
    resumeListeningFn?: () => void,
    skipPrefix: boolean = false
  ) => {
    if (!voiceEnabled) return;

    try {
      console.log(`🔊 Reading feedback with Azure Speech (${isCorrect ? 'correct' : 'incorrect'}) in ${languageCode}`);

      // PAUSE speech recognition to prevent hearing our own voice
      if (pauseListeningFn) {
        pauseListeningFn();
      }

      // Stop any currently playing audio first (including browser speech)
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
      
      // Stop browser speech synthesis
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel();
      }

      // Clear any previous progressive text display BEFORE starting new one
      clearProgressiveTextDisplay();

      // Generate feedback audio with secondary voice
      const audioResponse = await audioApi.generateFeedbackAudio(
        feedbackText,
        isCorrect,
        languageCode,
        skipPrefix
      );

      if (audioResponse?.audio_url) {
        // Start progressive text display if we have translated text
        if (audioResponse.translated_text) {
          const duration = audioResponse.duration_seconds || 3; // Default to 3 seconds for feedback
          startProgressiveTextDisplay(audioResponse.translated_text, duration);
        }

        // Play the generated audio
        const audio = new Audio(buildAudioUrl(audioResponse.audio_url));
        currentAudioRef.current = audio; // Store reference for stopping
        
        audio.onended = () => {
          console.log('🔊 Azure feedback speech completed');
          currentAudioRef.current = null;
          // Clear progressive text after a short delay
          setTimeout(() => {
            clearProgressiveTextDisplay();
            // NOTE: We do NOT auto-resume listening after feedback to prevent loops
            // User must manually click the mic button to continue giving commands
            console.log('🎤 Feedback complete. Click mic button to resume voice commands.');
          }, 2000);
        };
        
        audio.onerror = () => {
          console.error('🔊 Azure feedback speech failed, falling back to browser speech');
          currentAudioRef.current = null;
          clearProgressiveTextDisplay();
          // Do NOT auto-resume on error either
          fallbackToLocalSpeech(feedbackText);
        };

        await audio.play();
        console.log(`✅ Playing Azure feedback audio in ${languageCode}`);
      } else {
        throw new Error('No audio URL received');
      }

    } catch (error) {
      console.error('🔊 Azure feedback speech failed, falling back to browser speech:', error);
      currentAudioRef.current = null;
      clearProgressiveTextDisplay();
      // Do NOT auto-resume on error
      fallbackToLocalSpeech(feedbackText);
    }
  }, [voiceEnabled, selectedLanguage, fallbackToLocalSpeech, startProgressiveTextDisplay, clearProgressiveTextDisplay]);

  // Read question aloud using Azure Speech Service with multilingual support
  const readQuestion = useCallback(async () => {
    // Use the multilingual version with the selected language
    await readQuestionWithAzureSpeech(selectedLanguage);
  }, [readQuestionWithAzureSpeech, selectedLanguage]);

  // Stop reading
  const stopReading = useCallback(() => {
    console.log('🛑 stopReading called');
    
    // Stop HTML5 Audio element (Azure Speech)
    if (currentAudioRef.current) {
      console.log('🛑 Stopping current audio playback');
      try {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current = null;
      } catch (error) {
        console.error('Error stopping audio:', error);
        currentAudioRef.current = null;
      }
    }
    
    // Stop browser speech synthesis (fallback)
    if (speechSynthesisRef.current) {
      console.log('🛑 Cancelling speech synthesis');
      try {
        speechSynthesisRef.current.cancel();
      } catch (error) {
        console.error('Error cancelling speech synthesis:', error);
      }
    }
    
    // Also cancel any window.speechSynthesis that might be running
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
      console.log('🛑 Cancelling window speech synthesis');
      window.speechSynthesis.cancel();
    }
    
    // Clear progressive text display
    clearProgressiveTextDisplay();
    
    setIsReading(false);
    console.log('✅ stopReading completed');
  }, [clearProgressiveTextDisplay]);

  // Pause speech recognition temporarily (to prevent hearing our own audio feedback)
  const pauseListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        console.log('🎤 Pausing speech recognition to prevent feedback loop');
        recognitionRef.current.stop();
        setIsListening(false); // Update UI to show mic is off
        setCurrentTranscript(''); // Clear any current transcript
      } catch (error) {
        console.error('🎤 Failed to pause voice recognition:', error);
      }
    }
  }, [isListening]);

  // Resume speech recognition after audio finishes
  const resumeListening = useCallback(() => {
    if (recognitionRef.current && voiceEnabled && !isListening) {
      try {
        console.log('🎤 Resuming speech recognition after audio playback');
        recognitionRef.current.start();
      } catch (error) {
        console.error('🎤 Failed to resume voice recognition:', error);
      }
    }
  }, [voiceEnabled, isListening]);

  // Handle mouse/click-based answer selection with voice feedback
  const handleAnswerSelectWithFeedback = useCallback(async (answerId: string) => {
    const currentQuestion = assessment?.questions[currentQuestionIndex];
    if (!currentQuestion) return;

    // First, select the answer
    const selectedIndex = handleAnswerSelect(answerId);
    
    // Then provide voice feedback if enabled
    if (voiceEnabled && selectedIndex !== undefined && selectedIndex >= 0) {
      const feedbackText = `You selected option ${selectedIndex + 1}. Say "check answer" to verify, or "next question" to continue.`;
      
      // Use skipPrefix=true to avoid saying "Correct!" before checking the answer
      await readFeedbackWithAzureSpeech(feedbackText, true, selectedLanguage, pauseListening, resumeListening, true);
      
      // Inform user that they need to restart the mic
      setTimeout(() => {
        onSuccess('🎤 Click the microphone button to continue with voice commands');
      }, 3500); // Show after feedback audio completes
    }
  }, [assessment, currentQuestionIndex, handleAnswerSelect, voiceEnabled, selectedLanguage, readFeedbackWithAzureSpeech, pauseListening, resumeListening, onSuccess]);

  // Check answer - simple wrapper function
  const checkAnswer = useCallback(async () => {
    const currentQuestion = assessment?.questions[currentQuestionIndex];
    const currentState = getCurrentQuestionState();
    
    if (!currentQuestion || !currentState.isAnswered) {
      onError('Please select an answer first');
      return;
    }
    
    // Prevent duplicate checking if already checked
    if (currentState.isChecked) {
      console.log('Answer already checked, skipping duplicate check');
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
        ? 'Well done. Say "next question" to continue.' 
        : 'Please review the explanation. Say "next question" to continue.';
      
      // skipPrefix=false (default) will add "Correct!" or "Incorrect." prefix in the backend
      await readFeedbackWithAzureSpeech(feedbackText, isCorrect, selectedLanguage, pauseListening, resumeListening, false);
      
      // Inform user that they need to restart the mic
      setTimeout(() => {
        onSuccess('🎤 Click the microphone button to continue with voice commands');
      }, 3500); // Show after feedback audio completes
    }
    
    const message = isCorrect ? 'Correct answer!' : 'Incorrect answer. Please review the explanation.';
    if (isCorrect) {
      onSuccess(message);
    } else {
      onError(message);
    }
  }, [assessment, currentQuestionIndex, getCurrentQuestionState, updateQuestionState, voiceEnabled, onSuccess, onError, readFeedbackWithAzureSpeech, selectedLanguage, pauseListening, resumeListening]);

  // Handle voice commands
  const handleVoiceCommand = useCallback(async (transcript: string) => {
    if (!assessment) return;
    
    console.log('Voice command received:', transcript);
    
    // Get current language patterns
    const commandPatterns = getVoiceCommandPatterns(selectedLanguage);
    
    // Normalize transcript for better matching
    const normalizedTranscript = transcript.toLowerCase().trim();
    
    // Helper function to check if transcript contains any of the given patterns
    const containsAnyPattern = (patterns: string[]) => {
      return patterns.some(pattern => normalizedTranscript.includes(pattern));
    };
    
    // Check for "stop reading" command FIRST (before any other command)
    if (containsAnyPattern(commandPatterns.stopReading)) {
      stopReading();
      onSuccess('Stopped reading');
      return;
    }
    
    // Check for "read question" command
    if (containsAnyPattern(commandPatterns.readQuestion)) {
      // Stop any current reading before starting new one
      if (isReading) {
        stopReading();
      }
      await readQuestionWithAzureSpeech(selectedLanguage);
      return;
    }

    // Check for "check answer" command BEFORE "next question" to avoid confusion
    if (containsAnyPattern(commandPatterns.checkAnswer)) {
      // Use the existing checkAnswer function to avoid duplicate logic
      await checkAnswer();
      return;
    }
    
    // Check for "next question" command
    if (containsAnyPattern(commandPatterns.nextQuestion)) {
      const currentState = getCurrentQuestionState();
      
      if (!currentState.isAnswered) {
        onError('Please select an answer before moving to the next question');
        return;
      }
      
      // Remove the isChecked requirement - allow skipping answer checking
      // if (!currentState.isChecked) {
      //   onError('Please check your answer before moving to the next question');
      //   return;
      // }
      
      if (currentQuestionIndex < assessment.questions.length - 1) {
        const nextIndex = currentQuestionIndex + 1;
        setCurrentQuestionIndex(nextIndex);
        onSuccess('Moving to next question');
        
        // Automatically start reading the new question if voice is enabled
        if (voiceEnabled) {
          // Small delay to ensure the component has updated
          setTimeout(async () => {
            await readQuestionWithAzureSpeech(selectedLanguage, nextIndex); // Pass explicit index
          }, 500);
        }
      } else {
        onSuccess('You have completed all questions!');
      }
      return;
    }

    // Check for "previous question" command
    if (containsAnyPattern(commandPatterns.previousQuestion)) {
      if (currentQuestionIndex > 0) {
        const prevIndex = currentQuestionIndex - 1;
        setCurrentQuestionIndex(prevIndex);
        onSuccess('Moving to previous question');
        
        // Automatically start reading the new question if voice is enabled
        if (voiceEnabled) {
          setTimeout(async () => {
            await readQuestionWithAzureSpeech(selectedLanguage, prevIndex); // Pass explicit index
          }, 500);
        }
      } else {
        onSuccess('You are on the first question!');
      }
      return;
    }

    // Parse voice commands for options with multiple patterns
    const currentQuestion = assessment.questions[currentQuestionIndex];
    let optionNumber = -1;
    
    // Try multilingual patterns to match options
    for (const pattern of commandPatterns.optionPatterns) {
      const match = normalizedTranscript.match(pattern);
      if (match) {
        const captured = match[1];
        // Handle both letters (a,b,c,d,e,f) and numbers (1,2,3,4,5,6)
        if (/^[abcdef]$/i.test(captured)) {
          optionNumber = captured.toLowerCase().charCodeAt(0) - 'a'.charCodeAt(0);
        } else {
          optionNumber = parseInt(captured) - 1; // Convert to 0-based index
        }
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
        // Use skipPrefix=true to avoid saying "Correct!" before checking the answer
        await readFeedbackWithAzureSpeech(feedbackText, true, selectedLanguage, pauseListening, resumeListening, true);
        
        // Inform user that they need to restart the mic
        setTimeout(() => {
          onSuccess('🎤 Click the microphone button to continue with voice commands');
        }, 3000); // Show after feedback audio completes
      }
      return;
    }
    
    // If we get here, the command wasn't recognized
    console.log(`Unrecognized voice command: "${transcript}"`);
    onError(`Voice command not recognized. Try: "read question", "option 1-4", "check answer", "next question", or "stop"`);
  }, [assessment, currentQuestionIndex, isReading, stopReading, getCurrentQuestionState, handleAnswerSelect, voiceEnabled, onSuccess, onError, selectedLanguage, readQuestionWithAzureSpeech, readFeedbackWithAzureSpeech, checkAnswer, pauseListening, resumeListening]);

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
        setCurrentTranscript(''); // Clear transcript when stopping
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
    
    // Remove the isChecked requirement - allow skipping answer checking
    // if (!currentState.isChecked) {
    //   onError('Please check your answer before moving to the next question');
    //   return;
    // }
    
    if (currentQuestionIndex < (assessment?.questions.length || 0) - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      
      // Automatically start reading the new question if voice is enabled
      if (voiceEnabled) {
        // Small delay to ensure the component has updated
        setTimeout(async () => {
          await readQuestionWithAzureSpeech(selectedLanguage, nextIndex); // Pass explicit index
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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
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
              <FormControl size="small" sx={{ minWidth: 140 }}>
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

              {/* Real-time Transcription Display Toggle */}
              <FormControlLabel
                control={
                  <Switch
                    checked={showTranscription}
                    onChange={(e) => {
                      setShowTranscription(e.target.checked);
                      // Clear existing transcription if disabling
                      if (!e.target.checked) {
                        clearProgressiveTextDisplay();
                      }
                    }}
                    size="small"
                  />
                }
                label={
                  <Typography variant="caption" sx={{ whiteSpace: 'nowrap' }}>
                    Show Transcription
                  </Typography>
                }
              />

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

        {/* Progressive Transcription Display (Caption-style) */}
        {showTranscription && progressiveText && (
          <Box
            sx={{
              position: 'relative',
              mb: 2,
              p: 2.5,
              bgcolor: '#E3F2FD', // Light blue background
              minHeight: '60px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'fadeIn 0.3s ease-in',
              '@keyframes fadeIn': {
                from: { opacity: 0, transform: 'translateY(10px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
              }
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: '#1565C0', // Dark blue text
                fontWeight: 500,
                textAlign: 'center',
                lineHeight: 1.8,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                fontSize: '1.1rem'
              }}
            >
              {progressiveText}
            </Typography>
            
            {/* Typing indicator */}
            {progressiveText !== fullTranscriptionText && (
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: '8px',
                  height: '20px',
                  bgcolor: '#1565C0', // Dark blue cursor
                  ml: 0.5,
                  animation: 'blink 1s infinite',
                  '@keyframes blink': {
                    '0%, 50%': { opacity: 1 },
                    '51%, 100%': { opacity: 0 }
                  }
                }}
              />
            )}
          </Box>
        )}

        {/* Status Alerts */}
        {isReading && (
          <Alert severity="info" sx={{ mb: 1 }}>
            <Typography variant="body2">
              🔊 Reading question aloud in {selectedLanguage === 'en' ? 'English' : selectedLanguage.toUpperCase()}... 
              You can interrupt by saying a command or clicking "Stop Reading"
            </Typography>
          </Alert>
        )}
        
        {isListening && voiceEnabled && (
          <Alert severity="success" sx={{ mb: 1 }}>
            <Box>
              <Typography variant="body2" sx={{ mb: currentTranscript ? 1 : 0 }}>
                🎤 Listening for voice commands in {selectedLanguage.toUpperCase()}... 
                Say "read question", "option 1-4", "check answer", "next question", or "stop reading"
              </Typography>
              {currentTranscript && (
                <Box sx={{ 
                  mt: 1, 
                  p: 1.5, 
                  bgcolor: 'background.paper', 
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    Recognized Speech:
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    "{currentTranscript}"
                  </Typography>
                </Box>
              )}
            </Box>
          </Alert>
        )}
      </Paper>

      {/* Current Question */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" component="div" sx={{ mb: 3, lineHeight: 1.6 }}>
            {translatedQuestions.get(currentQuestionIndex) || currentQuestion.text}
          </Typography>

          {/* Answer Options */}
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend" sx={{ mb: 2 }}>
              Select your answer:
            </FormLabel>
            
            {currentQuestion.question_type === QuestionType.MULTIPLE_CHOICE ? (
              <RadioGroup
                value={currentState.selectedAnswers[0] || ''}
                onChange={(e) => handleAnswerSelectWithFeedback(e.target.value)}
              >
                {currentQuestion.answers.map((answer, index) => {
                  // Get translated answers if available, otherwise use original
                  const translatedAnswers = translatedAnswersMap.get(currentQuestionIndex);
                  const displayText = translatedAnswers?.[index] || answer.text;
                  
                  return (
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
                            {displayText}
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
                  );
                })}
              </RadioGroup>
            ) : (
              <FormGroup>
                {currentQuestion.answers.map((answer, index) => {
                  // Get translated answers if available, otherwise use original
                  const translatedAnswers = translatedAnswersMap.get(currentQuestionIndex);
                  const displayText = translatedAnswers?.[index] || answer.text;
                  
                  return (
                  <FormControlLabel
                    key={answer.id}
                    control={
                      <Checkbox
                        checked={currentState.selectedAnswers.includes(answer.id)}
                        onChange={(e) => {
                          handleAnswerSelectWithFeedback(answer.id);
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography component="span" sx={{ fontWeight: 'medium' }}>
                          Option {index + 1}:
                        </Typography>
                        <Typography component="span" sx={{ ml: 1 }}>
                          {displayText}
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
                  );
                })}
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
              • <Box component="strong" sx={{ display: 'inline' }}>"Stop reading"</Box> - Immediately stop the AI from reading
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Option 1", "Option 2", "Option 3", "Option 4"</Box> - Select answer options by voice or mouse
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Number 1", "Choice 2", "Answer 3"</Box> - Alternative ways to select options
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Check answer"</Box> - Verify if your selected answer is correct and view explanation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Next question"</Box> - Move to the next question (checking answer is optional)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • <Box component="strong" sx={{ display: 'inline' }}>"Previous question"</Box> - Go back to the previous question
            </Typography>
            <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic', color: 'info.dark' }}>
              💡 Tip: The microphone automatically turns off after AI speaks. Click the microphone icon to resume voice commands. Both mouse and voice selection trigger AI feedback.
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Footer */}
      <Box sx={{ mt: 6, pt: 4, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
        <Box sx={{ mb: 2 }}>
          <a 
            href="https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ textDecoration: 'none' }}
          >
            <Box 
              sx={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                gap: 1,
                px: 2,
                py: 1,
                borderRadius: 1,
                bgcolor: '#24292e',
                color: 'white',
                transition: 'all 0.3s',
                '&:hover': {
                  bgcolor: '#0969da',
                  transform: 'translateY(-2px)',
                  boxShadow: 2
                }
              }}
            >
              <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
              </svg>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                View on GitHub
              </Typography>
            </Box>
          </a>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          🌟 Open Source Project - We welcome contributions!
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Help us expand to <strong>AWS & GCP Official Practice Test Questions</strong>
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Powered by Azure AI Services | © 2025, All Rights Reserved!
        </Typography>
      </Box>
    </Box>
  );
};
export default AssessmentPage;
