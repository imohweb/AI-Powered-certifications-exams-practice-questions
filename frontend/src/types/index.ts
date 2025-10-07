/**
 * TypeScript type definitions for the Microsoft Certification Practice Assessment application.
 */

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  MULTIPLE_SELECT = 'multiple_select',
  TRUE_FALSE = 'true_false',
  DRAG_DROP = 'drag_drop',
  CASE_STUDY = 'case_study',
  HOTSPOT = 'hotspot'
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced'
}

export interface Answer {
  id: string;
  text: string;
  is_correct: boolean;
  explanation?: string;
}

export interface Question {
  id: string;
  text: string;
  question_type: QuestionType;
  answers: Answer[];
  correct_answer_ids: string[];
  explanation?: string;
  difficulty?: DifficultyLevel;
  topics: string[];
  reference_links: string[];
}

export interface PracticeAssessment {
  id: string;
  certification_code: string;
  title: string;
  description?: string;
  questions: Question[];
  total_questions: number;
  estimated_duration_minutes?: number;
  created_at: string;
  updated_at: string;
}

export interface UserSession {
  session_id: string;
  assessment_id: string;
  current_question_index: number;
  answered_questions: string[];
  score: number;
  start_time: string;
  last_activity: string;
  is_completed: boolean;
  auto_progression_enabled: boolean;
}

export interface UserAnswer {
  session_id: string;
  question_id: string;
  selected_answer_ids: string[];
  is_correct: boolean;
  time_spent_seconds?: number;
  answered_at: string;
}

export interface SessionProgress {
  session_id: string;
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  current_question_index: number;
  percentage_complete: number;
  score_percentage: number;
  estimated_time_remaining_minutes?: number;
}

export interface AudioRequest {
  text: string;
  voice_name?: string;
  speech_rate?: string;
  speech_pitch?: string;
  output_format?: string;
}

export interface AudioResponse {
  audio_url: string;
  duration_seconds?: number;
  cache_key?: string;
  translated_text?: string;  // Translated text for progressive display
  translated_question?: string;  // Translated question text only
  translated_answers?: string[];  // Translated answer options
}

export interface CertificationInfo {
  code: string;
  title: string;
  category?: string;
  level?: string;
  url?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface AnswerSubmissionResult {
  is_correct: boolean;
  correct_answer_ids: string[];
  explanation?: string;
  reference_links: string[];
  next_action: {
    action: 'auto_advance' | 'manual_advance' | 'complete_assessment' | 'error';
    delay_seconds?: number;
    message: string;
    auto_advance?: boolean;
  };
  progress: SessionProgress;
}

export interface SessionSummary {
  session_id: string;
  assessment_title: string;
  completion_status: 'completed' | 'in_progress';
  total_time_spent_minutes: number;
  progress: SessionProgress;
  topic_performance: Record<string, {
    total: number;
    correct: number;
    percentage: number;
  }>;
  difficulty_performance: Record<string, {
    total: number;
    correct: number;
    percentage: number;
  }>;
  recommendations: string[];
  detailed_answers: UserAnswer[];
}

export interface Voice {
  name: string;
  gender: string;
  locale: string;
  neural: boolean;
}

export interface VoicesResponse {
  voices: Record<string, Voice>;
  default_voice: string;
  total_count: number;
}

// Component Props Types
export interface QuestionCardProps {
  question: Question;
  selectedAnswers: string[];
  onAnswerSelect: (answerId: string) => void;
  showExplanation?: boolean;
  isSubmitted?: boolean;
}

export interface AudioPlayerProps {
  audioUrl?: string;
  autoPlay?: boolean;
  onPlayComplete?: () => void;
  onError?: (error: string) => void;
}

export interface ProgressBarProps {
  progress: SessionProgress;
  className?: string;
}

export interface CertificationSelectorProps {
  certifications: CertificationInfo[];
  selectedCertification?: string;
  onSelect: (certificationCode: string) => void;
  loading?: boolean;
}

// App State Types
export interface AppState {
  currentSession?: UserSession;
  currentQuestion?: Question;
  currentAssessment?: PracticeAssessment;
  loading: boolean;
  error?: string;
  audioEnabled?: boolean;
}

export interface AudioState {
  isPlaying: boolean;
  currentAudioUrl?: string;
  volume: number;
  playbackRate: number;
  autoPlay: boolean;
}

// API Error Types
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}