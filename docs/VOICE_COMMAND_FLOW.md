# Voice Command System Flow Diagram

## Complete Voice Command Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER STARTS ASSESSMENT                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │  Question Displayed     │
                        │  Voice Toggle: ON/OFF   │
                        └─────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ User Enables Voice?     │
                        └─────────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                       NO                          YES
                        │                           │
                        ▼                           ▼
              ┌──────────────────┐    ┌─────────────────────────────┐
              │ Manual Selection │    │ Click Microphone Button     │
              │ (Mouse/Keyboard) │    │ 🎤 Mic ON (Green Icon)      │
              └──────────────────┘    └─────────────────────────────┘
                        │                           │
                        │                           ▼
                        │             ┌─────────────────────────────┐
                        │             │ Speech Recognition Active   │
                        │             │ - Continuous listening      │
                        │             │ - Language: Selected Lang   │
                        │             │ - Display: "Listening..."   │
                        │             └─────────────────────────────┘
                        │                           │
                        └───────────────────────────┤
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                   VOICE INPUT                 MANUAL INPUT
                        │                           │
                        ▼                           │
        ┌───────────────────────────────┐          │
        │ VOICE COMMAND PROCESSING      │          │
        └───────────────────────────────┘          │
                        │                           │
        ┌───────────────┴───────────────┐          │
        │                               │          │
        ▼                               ▼          │
┌──────────────────┐         ┌──────────────────┐ │
│ "Read Question"  │         │ "Option 1-4"     │ │
│ Command          │         │ Command          │ │
└──────────────────┘         └──────────────────┘ │
        │                               │          │
        ▼                               ▼          │
┌──────────────────┐         ┌──────────────────┐ │
│ AI Reads Full    │         │ Select Option    │◄┘
│ Question + All   │         │ (Voice or Mouse) │
│ Answer Options   │         └──────────────────┘
└──────────────────┘                   │
        │                               ▼
        │                 ┌───────────────────────────────┐
        │                 │ OPTION SELECTED               │
        │                 │ State: isAnswered = true      │
        │                 └───────────────────────────────┘
        │                               │
        │                               ▼
        │                 ┌───────────────────────────────┐
        │                 │ PAUSE Speech Recognition      │
        │                 │ 🎤 Mic OFF (Red Icon)         │
        │                 └───────────────────────────────┘
        │                               │
        │                               ▼
        │                 ┌───────────────────────────────┐
        │                 │ AI Voice Feedback:            │
        │                 │ "You selected option X.       │
        │                 │  Say 'check answer' to        │
        │                 │  verify, or 'next question'   │
        │                 │  to continue."                │
        │                 │ [skipPrefix=true → NO         │
        │                 │  "Correct!" prefix]           │
        │                 └───────────────────────────────┘
        │                               │
        │                               ▼
        │                 ┌───────────────────────────────┐
        │                 │ Display Notification:         │
        │                 │ "🎤 Click microphone to       │
        │                 │  continue with voice"         │
        │                 └───────────────────────────────┘
        │                               │
        │                               ▼
        │                 ┌───────────────────────────────┐
        │                 │ USER MUST MANUALLY RESTART    │
        │                 │ Click Microphone Button Again │
        │                 │ 🎤 Mic ON (Green Icon)        │
        │                 └───────────────────────────────┘
        │                               │
        └───────────────────────────────┤
                                        │
                        ┌───────────────┴───────────────┐
                        │                               │
                   VOICE INPUT                    BUTTON CLICK
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────┐
        │ "Check Answer" Voice Command  │   │ "Check Answer"   │
        │                               │   │ Button Click     │
        └───────────────────────────────┘   └──────────────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │ VALIDATE & CHECK ANSWER       │
                        │ - Compare with correct answer │
                        │ - Update state: isChecked=true│
                        │ - Show explanation if wrong   │
                        └───────────────────────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        │                               │
                    CORRECT                         INCORRECT
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────────────┐
        │ PAUSE Speech Recognition      │   │ PAUSE Speech Recognition │
        │ 🎤 Mic OFF                    │   │ 🎤 Mic OFF               │
        └───────────────────────────────┘   └──────────────────────────┘
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────────────┐
        │ AI Voice Feedback:            │   │ AI Voice Feedback:       │
        │ "Correct! Well done.          │   │ "Incorrect. Please       │
        │  Say 'next question' to       │   │  review the explanation. │
        │  continue."                   │   │  Say 'next question' to  │
        │ [skipPrefix=false → Backend   │   │  continue."              │
        │  adds "Correct!" prefix]      │   │ [skipPrefix=false]       │
        └───────────────────────────────┘   └──────────────────────────┘
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────────────┐
        │ Display Notification:         │   │ Display Notification:    │
        │ "🎤 Click microphone to       │   │ "🎤 Click microphone to  │
        │  continue with voice"         │   │  continue with voice"    │
        └───────────────────────────────┘   └──────────────────────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │ Show Results & Explanation    │
                        │ - Green checkmark if correct  │
                        │ - Red X if incorrect          │
                        │ - Display explanation         │
                        └───────────────────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │ USER MANUALLY RESTARTS MIC    │
                        │ Click Microphone Button       │
                        │ 🎤 Mic ON (Green Icon)        │
                        └───────────────────────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        │                               │
                   VOICE INPUT                    BUTTON CLICK
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────┐
        │ "Next Question" Voice Command │   │ "Next Question"  │
        │                               │   │ Button Click     │
        └───────────────────────────────┘   └──────────────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │ Validate Navigation           │
                        │ - Check if answer checked     │
                        │ - Check if not last question  │
                        └───────────────────────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        │                               │
                   VALIDATED                       INVALID
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────────┐   ┌──────────────────────────┐
        │ Move to Next Question         │   │ Show Error Message:      │
        │ - Increment question index    │   │ "Please check answer     │
        │ - Reset answer state          │   │  first" OR               │
        │ - Load new question           │   │ "Last question reached"  │
        └───────────────────────────────┘   └──────────────────────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │ LOOP BACK TO QUESTION         │
                        │ DISPLAY (Top of Flow)         │
                        └───────────────────────────────┘
```

---

## Voice Command Recognition & Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SPEECH RECOGNITION ACTIVE                              │
│                      (After User Clicks Mic Button)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Browser Web Speech API      │
                        │ - Language: selectedLanguage│
                        │ - Continuous: true          │
                        │ - InterimResults: false     │
                        │ - MaxAlternatives: 5        │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ User Speaks Command         │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Audio Captured → Transcript │
                        │ Display: Current Transcript │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Normalize Transcript:       │
                        │ - Convert to lowercase      │
                        │ - Trim whitespace           │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ COMMAND PATTERN MATCHING    │
                        └─────────────────────────────┘
                                      │
        ┌─────────────┬───────────────┼───────────────┬─────────────┬──────────────┐
        │             │               │               │             │              │
        ▼             ▼               ▼               ▼             ▼              ▼
┌───────────┐  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│"read      │  │"stop       │  │"option   │  │"check     │  │"next     │  │"previous │
│ question" │  │ reading"   │  │ 1-4"     │  │ answer"   │  │ question"│  │ question"│
└───────────┘  └────────────┘  └──────────┘  └───────────┘  └──────────┘  └──────────┘
      │              │               │               │             │              │
      ▼              ▼               ▼               ▼             ▼              ▼
┌───────────┐  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│Stop any   │  │Stop all    │  │Parse     │  │Validate & │  │Check if  │  │Check if  │
│current    │  │audio       │  │option    │  │check      │  │answer    │  │not first │
│reading    │  │playback    │  │number    │  │answer     │  │checked   │  │question  │
└───────────┘  └────────────┘  └──────────┘  └───────────┘  └──────────┘  └──────────┘
      │              │               │               │             │              │
      ▼              ▼               ▼               ▼             ▼              ▼
┌───────────┐  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│Generate   │  │Clear text  │  │Select    │  │Show result│  │Navigate  │  │Navigate  │
│multi-     │  │display     │  │answer    │  │+ feedback │  │forward   │  │backward  │
│lingual    │  │Set mic ON  │  │option    │  │voice      │  │+ auto-   │  │+ auto-   │
│audio      │  │Success msg │  │Give voice│  │Turn OFF   │  │read if   │  │read if   │
│Keep mic   │  └────────────┘  │feedback  │  │mic        │  │voice ON  │  │voice ON  │
│ON         │                  │Turn OFF  │  └───────────┘  └──────────┘  └──────────┘
└───────────┘                  │mic       │
                               └──────────┘
```

---

## Audio Feedback Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   VOICE FEEDBACK REQUEST                                    │
│              (readFeedbackWithAzureSpeech called)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Parameters:                 │
                        │ - feedbackText              │
                        │ - isCorrect (true/false)    │
                        │ - languageCode              │
                        │ - skipPrefix (true/false)   │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ PAUSE Speech Recognition    │
                        │ pauseListening()            │
                        │ - Stop mic listening        │
                        │ - Set isListening = false   │
                        │ - Update UI (mic OFF icon)  │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Stop Current Audio/Speech   │
                        │ - Pause HTML5 Audio         │
                        │ - Cancel Speech Synthesis   │
                        │ - Clear progressive text    │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ API Call: POST /audio/      │
                        │ generate/feedback           │
                        │ - feedback_text             │
                        │ - is_correct                │
                        │ - language_code             │
                        │ - skip_prefix ⭐ NEW        │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ BACKEND PROCESSING          │
                        └─────────────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                  skip_prefix=true            skip_prefix=false
                        │                           │
                        ▼                           ▼
        ┌───────────────────────────┐   ┌──────────────────────────┐
        │ Use feedback text AS IS   │   │ Add prefix to text:      │
        │ "You selected option 1.   │   │ IF isCorrect=true:       │
        │  Say 'check answer'..."   │   │   "Correct! {text}"      │
        │                           │   │ IF isCorrect=false:      │
        │ (For option selection)    │   │   "Incorrect. {text}"    │
        │                           │   │                          │
        │                           │   │ (For answer validation)  │
        └───────────────────────────┘   └──────────────────────────┘
                        │                           │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Translate if needed         │
                        │ (Azure Translator Service)  │
                        │ - Source: English           │
                        │ - Target: languageCode      │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Select Voice:               │
                        │ - Secondary voice (Aria)    │
                        │ - Language-specific voice   │
                        │   for non-English           │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Generate Audio with Azure   │
                        │ Speech Service (SSML)       │
                        │ - Speech rate: 1.1x         │
                        │ - Speech pitch: +2Hz        │
                        │ - Emotional context         │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Cache Audio                 │
                        │ - Hash: MD5(text+lang+voice)│
                        │ - Store: audio_cache/       │
                        │ - Return: /audio/cache/{id} │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ FRONTEND RECEIVES RESPONSE  │
                        │ - audio_url                 │
                        │ - translated_text           │
                        │ - duration_seconds          │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Start Progressive Text      │
                        │ Display (Caption-style)     │
                        │ - Word-by-word display      │
                        │ - Sync with audio duration  │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Play Audio                  │
                        │ - HTML5 Audio element       │
                        │ - Base URL + audio_url      │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Audio Playback Monitoring   │
                        └─────────────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                   audio.onended              audio.onerror
                        │                           │
                        ▼                           ▼
        ┌───────────────────────────┐   ┌──────────────────────────┐
        │ Clear Audio Reference     │   │ Clear Audio Reference    │
        │ Wait 2 seconds            │   │ Clear text display       │
        │ Clear text display        │   │ Fallback to browser      │
        │ Log completion            │   │ speech synthesis         │
        │                           │   │                          │
        │ ⚠️ DO NOT auto-resume    │   │ ⚠️ DO NOT auto-resume   │
        │    speech recognition     │   │    speech recognition    │
        └───────────────────────────┘   └──────────────────────────┘
                        │                           │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Show Notification:          │
                        │ "🎤 Click microphone button │
                        │  to continue with voice     │
                        │  commands"                  │
                        └─────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │ Wait for User Action        │
                        │ (Manual mic button click)   │
                        └─────────────────────────────┘
```

---

## Key Features & Anti-Feedback Loop Mechanisms

### 1. **Microphone Auto-Pause During Feedback**
```
Voice Command → PAUSE Mic → Play Feedback → Keep Mic OFF → Wait for Manual Restart
```
- Prevents mic from hearing AI's own voice
- Eliminates feedback loops
- User has full control over when to resume

### 2. **Skip Prefix Logic**
```
Option Selection → skipPrefix=true  → "You selected option 1..."
Answer Check    → skipPrefix=false → "Correct! Well done..."
```
- Prevents premature "Correct!" message
- Maintains logical feedback flow

### 3. **Progressive Text Display**
```
Audio Playing → Word-by-Word Display → Synced with Audio Duration
```
- Visual feedback during audio playback
- Clears before new audio starts
- Prevents text accumulation

### 4. **State Management**
```
isListening: boolean     → Mic ON/OFF state
isReading: boolean       → Audio playback state  
isAnswered: boolean      → Option selected state
isChecked: boolean       → Answer validated state
progressiveText: string  → Current caption text
```

---

## Supported Voice Commands

| Command | Pattern | Function |
|---------|---------|----------|
| Read Question | "read question", "read the question", "repeat question" | Reads full question + all options |
| Stop Reading | "stop reading", "stop", "pause", "quiet" | Stops current audio playback |
| Select Option | "option 1-4", "number 1", "choice 2", "first", "second" | Selects answer option |
| Check Answer | "check answer", "verify answer", "submit answer" | Validates selected answer |
| Next Question | "next question", "next" | Navigates to next question (if answered & checked) |
| Previous Question | "previous question", "previous", "go back" | Navigates to previous question |

---

## Error Handling & Edge Cases

### 1. **Microphone Permission Denied**
```
User denies mic → Show error → Disable voice features → Manual input only
```

### 2. **No Speech Detected**
```
Timeout → Continue listening → No error shown → Auto-restart
```

### 3. **Command Not Recognized**
```
Unknown speech → Show error: "Voice command not recognized. Try: ..." → Keep listening
```

### 4. **Audio Playback Failure**
```
Azure API fails → Fallback to browser Speech Synthesis API → Continue flow
```

### 5. **Network Error**
```
API timeout → Show error → Retry or fallback → Manual controls available
```

---

This flow ensures:
- ✅ No infinite feedback loops
- ✅ Logical question → answer → check → next flow
- ✅ User control over voice commands
- ✅ Multilingual support
- ✅ Robust error handling
