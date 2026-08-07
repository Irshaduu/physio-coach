/* ============================================================
   Therapist — Player Engine
   Speech-driven state machine for audio-visual workout guidance.
   ============================================================ */

(function () {
    'use strict';

    // ─── Constants ──────────────────────────────────────────
    const CIRCUMFERENCE = 2 * Math.PI * 88; // SVG circle r=88
    const EXERCISE_REST_SECONDS = 60;
    const USER_NAME = (window.Therapist_USER || '').trim() || null;

    // Helper: return name if available, else empty string
    const withName = (str) => USER_NAME ? str.replace('{name}', USER_NAME) : '';

    // ═══ i18n ═══════════════════════════════════════════════════════════
    const I18N = {
        en: {
            exercise: 'Exercise',
            rep: 'Rep',
            hold: 'Hold',
            relax: 'Relax',
            exerciseDone: 'And relax. Great job on that set.',
            nextUp: 'Next Up',
            restNext: (name) => `Take a deep breath and rest for a minute. Next up: ${name}.`,
            announce: (num, name, desc) => `Exercise ${num}. ${name}. ${desc}`,
            workoutComplete: USER_NAME
                ? `Amazing work, ${USER_NAME}! You have finished the entire routine for today. Your knee is getting stronger every day! Be proud!`
                : `Amazing work! You have finished the entire routine for today. Your knee is getting stronger every day! Be proud!`,
            testVoice: USER_NAME
                ? `Hello ${USER_NAME}! I am your PhysioCoach. I will be guiding you step-by-step through today's exercises. Let's get started!`
                : `Hello! I am your PhysioCoach. I will be guiding you step-by-step through today's exercises. Let's get started!`,
            readyTitle: 'Ready to Begin',
            readyDesc: "Press Start when you're ready.",
            phase_announce: 'ANNOUNCE',
            phase_hold: 'HOLD',
            phase_rest: 'RELAX',
            phase_exercise_rest: 'REST',
            phase_idle: 'IDLE',
            motivational: {
                phase_a: [ // Rep 1-7: Form & Focus
                    "Keep breathing, smooth and steady.",
                    "You are doing great, don't rush it.",
                    "Focus on the movement, not the count.",
                    "Your form is perfect right now.",
                    "Don't hold your breath, keep the oxygen flowing.",
                    "Keep the knee stable. You are doing great.",
                    "Breathe deeply, let the oxygen fuel your muscles.",
                    "Feel that stretch? That is exactly what we want.",
                    "Beautiful form! Let's keep that going.",
                    "Take it one second at a time. No rush.",
                    "Keep your body aligned and straight.",
                    "Every second of this hold is building stability.",
                    "Breathe in gently, breathe out slowly.",
                    "Smooth movements, don't jerk the knee.",
                    "Great start! Keep this exact rhythm.",
                    ...(USER_NAME ? [
                        `${USER_NAME}, you have incredible focus today.`,
                        `Look at that form, ${USER_NAME}. Excellent work.`,
                        `Nice posture, ${USER_NAME}. Keep it steady.`,
                        `You are doing this perfectly, ${USER_NAME}.`
                    ] : [
                        "You have incredible focus today.",
                        "Look at that form. Excellent work.",
                        "Nice posture. Keep it steady.",
                        "You are doing this perfectly."
                    ])
                ],
                phase_b: [ // Rep 8-15: Consistency & Pushing Through
                    "Feel the burn? That is your knee getting stronger.",
                    "Excellent control. Keep it up.",
                    "I know it is tough, but you are doing exactly what you need to do.",
                    "Every single rep is a step towards full recovery.",
                    "You are doing this for yourself. Keep going.",
                    "Almost halfway, keep pushing!",
                    "That is it, exactly like that.",
                    "Consistency is the key to recovery, and you are nailing it.",
                    "Every small movement is a big victory for your knee.",
                    "You are on the right track. Don't stop now.",
                    "The discomfort means the muscles are waking up.",
                    "We are halfway through this exercise, don't quit.",
                    "Your joints are getting the support they need.",
                    "If you feel tired, take a deeper breath.",
                    "You are moving forward beautifully.",
                    ...(USER_NAME ? [
                        `I am so proud of your consistency, ${USER_NAME}.`,
                        `I see that effort, ${USER_NAME}. Keep it up!`,
                        `Your progress is truly inspiring, ${USER_NAME}.`,
                        `Keep that energy up, ${USER_NAME}.`,
                        `I know it burns, ${USER_NAME}, but you are doing great.`
                    ] : [
                        "I am so proud of your consistency.",
                        "I see that effort. Keep it up!",
                        "Your progress is truly inspiring.",
                        "Keep that energy up.",
                        "I know it burns, but you are doing great."
                    ])
                ],
                phase_c: [ // Rep 16-20: Finishing Strong
                    "You are incredibly resilient.",
                    "I am right here with you. Let us finish strong.",
                    "This is where the magic happens, keep working.",
                    "Your body is healing, trust the process.",
                    "A little effort today brings a lot of relief tomorrow.",
                    "Don't let the fatigue win. You are stronger.",
                    "That is perfect execution. Well done.",
                    "Your muscles are adapting and getting stronger.",
                    "You are proving to yourself how tough you are.",
                    "Recovery takes patience, and you are doing brilliantly.",
                    "Just a handful left! Let's make them count.",
                    "The last few are always the most important.",
                    "Your knee is getting its strength back, almost done!",
                    "We are going to complete this set successfully!",
                    "Perfect! You'll get to relax in just a moment.",
                    ...(USER_NAME ? [
                        `Stay strong, ${USER_NAME}. We are almost done with this set.`,
                        `You've got this, ${USER_NAME}. Don't give up now!`,
                        `Let's finish this set together, ${USER_NAME}.`,
                        `You are doing something amazing for your body today, ${USER_NAME}.`,
                        `${USER_NAME}, you are crushing this workout!`,
                        `Finish strong, ${USER_NAME}! I'm right here with you.`,
                        `Push through these last few, ${USER_NAME}!`
                    ] : [
                        "Stay strong. We are almost done with this set.",
                        "You've got this. Don't give up now!",
                        "Let's finish this set together.",
                        "You are doing something amazing for your body today.",
                        "You are crushing this workout!",
                        "Finish strong! I'm right here with you.",
                        "Push through these last few!"
                    ])
                ]
            }
        },
        ml: {
            exercise: 'വ്യായാമം',
            rep: 'റെപ്',
            hold: 'പിടിക്കൂ',
            relax: 'ആശ്വസിക്കൂ',
            exerciseDone: 'ആശ്വസിക്കൂ. ഈ വ്യായാമം വളരെ നന്നായി ചെയ്തു.',
            restNext: (name) => `നന്നായി ചെയ്തു. ഇനി ഒരു മിനിറ്റ് വിശ്രമിക്കാം കേട്ടോ. അടുത്തത്: ${name}.`,
            announce: (num, name, desc) => `വ്യായാമം ${num}. ${name}. ${desc}`,
            workoutComplete: USER_NAME
                ? `ഗംഭീരം ${USER_NAME}! ഇന്നത്തെ വ്യായാമങ്ങൾ എല്ലാം നമ്മൾ വിജയകരമായി പൂർത്തിയാക്കിയിരിക്കുന്നു. നിങ്ങളുടെ മുട്ടിന്റെ ആരോഗ്യം മെച്ചപ്പെട്ടുകൊണ്ടിരിക്കുകയാണ് കേട്ടോ!`
                : `ഗംഭീരം! ഇന്നത്തെ വ്യായാമങ്ങൾ എല്ലാം നമ്മൾ വിജയകരമായി പൂർത്തിയാക്കിയിരിക്കുന്നു. നിങ്ങളുടെ മുട്ടിന്റെ ആരോഗ്യം മെച്ചപ്പെട്ടുകൊണ്ടിരിക്കുകയാണ് കേട്ടോ!`,
            testVoice: USER_NAME
                ? `നമസ്കാരം ${USER_NAME}! ഞാൻ നിങ്ങളുടെ സ്വന്തം ഫിസിയോ കോച്ച് ആണ്. ഇന്നത്തെ വ്യായാമങ്ങൾ നമുക്ക് ഒരുമിച്ച് ചെയ്യാം. റെഡി അല്ലേ?`
                : `നമസ്കാരം! ഞാൻ നിങ്ങളുടെ സ്വന്തം ഫിസിയോ കോച്ച് ആണ്. ഇന്നത്തെ വ്യായാമങ്ങൾ നമുക്ക് ഒരുമിച്ച് ചെയ്യാം. റെഡി അല്ലേ?`,
            readyTitle: 'തുടങ്ങാൻ തയ്യാറാണ്',
            readyDesc: 'തയ്യാറാകുമ്പോൾ Start ബട്ടൺ അമർത്തുക.',
            nextUp: 'അടുത്തത്',
            phase_announce: 'ഒരുങ്ങൂ',
            phase_hold: 'പിടിക്കൂ',
            phase_rest: 'വിശ്രമിക്കൂ',
            phase_exercise_rest: 'വിശ്രമിക്കാം',
            phase_idle: 'കാത്തിരിക്കൂ',
            motivational: {
                phase_a: [
                    "നന്നായി ചെയ്യുന്നുണ്ട്, ധൃതി വെക്കണ്ട പതുക്കെ മതി.",
                    "വളരെ നല്ല ഫോം ആണ്, ഇതേപോലെ തന്നെ ചെയ്യാം.",
                    "ശ്വാസം നന്നായി എടുത്ത് വിടണം കേട്ടോ, പിടിച്ചു വെക്കരുത്.",
                    "ആ ശ്രദ്ധ അങ്ങനെ തന്നെ നിൽക്കട്ടെ, വളരെ നല്ലത്.",
                    "മുട്ട് അനങ്ങാതെ സൂക്ഷിക്കണം കേട്ടോ. നന്നായി ചെയ്യുന്നുണ്ട്.",
                    "പതുക്കെ മതി, ഒട്ടും ധൃതി വെക്കേണ്ട.",
                    "നന്നായി ശ്വാസമെടുക്കൂ, പേശികൾക്ക് അത് നല്ലതാണ്.",
                    "ആ വലിഞ്ഞുമുറുകൽ തോന്നുന്നുണ്ടോ? അത് വളരെ നല്ലതാണ്.",
                    "വളരെ കൃത്യമായിട്ടാണ് ചെയ്യുന്നത്. വളരെ നല്ലത്.",
                    "അടിപൊളി! ഇങ്ങനെ തന്നെ തുടരാം.",
                    "ശരീരം നേരെ വെക്കാൻ പ്രത്യേകം ശ്രദ്ധിക്കുക.",
                    "ഓരോ സെക്കൻഡും പ്രധാനമാണ്, കൃത്യമായി ചെയ്യുക.",
                    "ശ്വാസം ഉള്ളിലേക്ക് എടുത്ത് പതിയെ പുറത്തേക്ക് വിടുക.",
                    "മുട്ടിന് അധികം സ്ട്രെസ് കൊടുക്കരുത്, സ്മൂത്ത് ആയി ചെയ്യാം.",
                    "തുടക്കം ഗംഭീരമായിട്ടുണ്ട്! ഇതേ രീതിയിൽ തുടരാം.",
                    ...(USER_NAME ? [
                        `${USER_NAME}, വളരെ നന്നായി ചെയ്യുന്നുണ്ട് കേട്ടോ.`,
                        `${USER_NAME}, നിങ്ങൾ ഇന്ന് വളരെ ഉഷാറാണല്ലോ!`,
                        `${USER_NAME}, വളരെ നല്ല പോസ്ചർ ആണ് കേട്ടോ.`,
                        `ഇങ്ങനെ തന്നെ മതി ${USER_NAME}, ഉഷാറായിട്ടുണ്ട്.`
                    ] : [
                        "വളരെ നന്നായി ചെയ്യുന്നുണ്ട് കേട്ടോ.",
                        "നിങ്ങൾ ഇന്ന് വളരെ ഉഷാറാണല്ലോ!",
                        "വളരെ നല്ല പോസ്ചർ ആണ് കേട്ടോ.",
                        "ഇങ്ങനെ തന്നെ മതി, ഉഷാറായിട്ടുണ്ട്."
                    ])
                ],
                phase_b: [
                    "മുട്ടിന് നല്ല ആശ്വാസം കിട്ടും, കുറച്ചുകൂടി.",
                    "വേദനയുണ്ടോ? പേടിക്കണ്ട, ഇത് മാറും.",
                    "ഓരോ തവണ ചെയ്യുമ്പോഴും മുട്ടിന്റെ ബലം കൂടുകയാണ്.",
                    "ബുദ്ധിമുട്ടാണെന്ന് എനിക്കറിയാം, പക്ഷെ നന്നായി ചെയ്യുന്നുണ്ട്.",
                    "ഇത് നിങ്ങൾ നിങ്ങൾക്ക് വേണ്ടി ചെയ്യുന്നതാണ്, നിർത്തരുത്.",
                    "പകുതി കഴിഞ്ഞു, ഇനി കുറച്ചുകൂടി മാത്രം.",
                    "ഇങ്ങനെ തന്നെ മതി, വളരെ കറക്റ്റ് ആണ്.",
                    "തുടർച്ചയായുള്ള ഈ പരിശ്രമമാണ് പെട്ടെന്ന് സുഖം തരിക.",
                    "ഓരോ ചെറിയ ചലനവും വലിയൊരു മാറ്റത്തിലേക്കാണ്.",
                    "നിങ്ങൾ ശരിയായ വഴിയിലാണ്. ഇനി നിർത്തരുത്.",
                    "ഇപ്പോൾ കുറച്ചു വേദന തോന്നും, പക്ഷെ അത് പേശികൾ ഉണരുന്നതിന്റെ ലക്ഷണമാണ്.",
                    "പകുതി ദൂരം നമ്മൾ പിന്നിട്ടു, ഇനി വിട്ടുകൊടുക്കരുത്.",
                    "നിങ്ങളുടെ കാൽമുട്ടിന് ഇപ്പോൾ നല്ല ഉറപ്പ് കിട്ടുന്നുണ്ട്.",
                    "ക്ഷീണം തോന്നുണ്ടെങ്കിൽ ദീർഘമായി ഒന്ന് ശ്വാസമെടുക്കൂ.",
                    "വളരെ നന്നായിട്ട് മുന്നോട്ട് പോകുന്നുണ്ട്.",
                    ...(USER_NAME ? [
                        `${USER_NAME}, നിങ്ങളുടെ ഈ പരിശ്രമം ഞാൻ കാണുന്നുണ്ട്. വളരെ നല്ലത്!`,
                        `${USER_NAME}, നിങ്ങളുടെ മാറ്റം ശരിക്കും അത്ഭുതപ്പെടുത്തുന്നതാണ് കേട്ടോ.`,
                        `ഇത്രയും ചെയ്തത് വലിയ കാര്യമാണ് ${USER_NAME}, ഇനി കുറച്ചുകൂടി.`,
                        `ആ എനർജി അങ്ങനെ തന്നെ നിൽക്കട്ടെ ${USER_NAME}.`,
                        `കുറച്ചു ബുദ്ധിമുട്ടുണ്ടാകും ${USER_NAME}, പക്ഷെ വിടരുത്.`
                    ] : [
                        "നിങ്ങളുടെ ഈ പരിശ്രമം ഞാൻ കാണുന്നുണ്ട്. വളരെ നല്ലത്!",
                        "നിങ്ങളുടെ മാറ്റം ശരിക്കും അത്ഭുതപ്പെടുത്തുന്നതാണ് കേട്ടോ.",
                        "ഇത്രയും ചെയ്തത് വലിയ കാര്യമാണ്, ഇനി കുറച്ചുകൂടി.",
                        "ആ എനർജി അങ്ങനെ തന്നെ നിൽക്കട്ടെ.",
                        "കുറച്ചു ബുദ്ധിമുട്ടുണ്ടാകും, പക്ഷെ വിടരുത്."
                    ])
                ],
                phase_c: [
                    "നിങ്ങളുടെ ഈ പരിശ്രമം തീർച്ചയായും ഫലം തരും.",
                    "ഞാൻ കൂടെത്തന്നെയുണ്ട്, നമുക്കിത് ഒരുമിച്ച് തീർക്കാം.",
                    "ഇപ്പോഴാണ് പേശികൾക്ക് ശരിക്കും വ്യായാമം കിട്ടുന്നത്, തുടരുക.",
                    "ക്ഷീണിച്ചോ? സാരമില്ല, കുറച്ചു കൂടി കഴിഞ്ഞാൽ വിശ്രമിക്കാം.",
                    "ശരീരം പതുക്കെ ഭേദമായി വരികയാണ്, ഈ മാറ്റം വിശ്വസിക്കൂ.",
                    "ഇന്നത്തെ ചെറിയൊരു കഷ്ടപ്പാട് നാളത്തെ വലിയൊരു ആശ്വാസമാണ്.",
                    "ക്ഷീണം തോന്നിയാലും വിട്ടുകൊടുക്കരുത്, നിങ്ങൾക്കതിന് സാധിക്കും.",
                    "പേശികൾക്ക് പതുക്കെ ബലം വെച്ച് വരികയാണ്.",
                    "നിങ്ങൾക്ക് എത്രത്തോളം ചെയ്യാൻ കഴിയുമെന്ന് നിങ്ങൾ തന്നെ തെളിയിക്കുകയാണ്.",
                    "കുറച്ചു ക്ഷമയൊക്കെ വേണ്ടിവരും, പക്ഷെ നിങ്ങൾ നന്നായി ചെയ്യുന്നുണ്ട്.",
                    "ഇനി വിരലിലെണ്ണാവുന്നവ മാത്രം! പവർ വരട്ടെ!",
                    "അവസാനത്തെ കുറച്ചെണ്ണം എപ്പോഴും സ്പെഷ്യൽ ആണ്, പൊളിക്കാം!",
                    "മുട്ടിന്റെ പഴയ പവർ തിരിച്ചു വരികയാണ്, തീരാറായി!",
                    "ഈ സെറ്റ് നമ്മൾ വിജയകരമായി പൂർത്തിയാക്കാൻ പോകുന്നു!",
                    "പെർഫെക്റ്റ്! ഇനി ഒന്ന് റിലാക്സ് ചെയ്യാൻ സമയമായി.",
                    ...(USER_NAME ? [
                        `${USER_NAME}, ഈ ഒരു നിശ്ചയദാർഢ്യം സമ്മതിക്കണം.`,
                        `വിടരുത് ${USER_NAME}, നമുക്കിത് മുഴുവനാക്കണം.`,
                        `${USER_NAME}, നിങ്ങൾ വളരെ മികച്ച രീതിയിലാണ് ചെയ്യുന്നത്!`,
                        `${USER_NAME}, ശരീരത്തിന് വേണ്ടി വളരെ നല്ലൊരു കാര്യമാണ് ഇന്ന് ചെയ്യുന്നത്.`,
                        `${USER_NAME}, നമുക്കീ സെറ്റ് ഒരുമിച്ച് തീർക്കാം കേട്ടോ.`,
                        `അവസാനത്തെ കുറച്ചെണ്ണം നമുക്ക് പവറിൽ തീർക്കാം ${USER_NAME}!`,
                        `ഗംഭീരം ${USER_NAME}! ഇനി കുറച്ചുകൂടി മാത്രം!`
                    ] : [
                        "നിങ്ങളുടെ ഈ നിശ്ചയദാർഢ്യം സമ്മതിക്കണം.",
                        "വിടരുത്, നമുക്കിത് മുഴുവനാക്കണം.",
                        "നിങ്ങൾ വളരെ മികച്ച രീതിയിലാണ് ചെയ്യുന്നത്!",
                        "ശരീരത്തിന് വേണ്ടി വളരെ നല്ലൊരു കാര്യമാണ് ഇന്ന് ചെയ്യുന്നത്.",
                        "നമുക്കീ സെറ്റ് ഒരുമിച്ച് തീർക്കാം കേട്ടോ.",
                        "അവസാനത്തെ കുറച്ചെണ്ണം നമുക്ക് പവറിൽ തീർക്കാം!",
                        "ഗംഭീരം! ഇനി കുറച്ചുകൂടി മാത്രം!"
                    ])
                ]
            }
        },
        };

    function t(key) {
        return I18N[currentLang][key] || I18N['en'][key];
    }

    function getName(ex) {
        return currentLang === 'ml' ? (ex.name_ml || ex.name) : ex.name;
    }

    function getDesc(ex) {
        return currentLang === 'ml' ? (ex.description_ml || ex.description || '') : (ex.description || '');
    }

    // ─── State ──────────────────────────────────────────────
    let exercises = [];
    let currentExerciseIdx = 0;
    let currentRep = 0;
    let isPaused = false;
    let isRunning = false;
    let wakeLockSentinel = null;
    let selectedVoice = null;
    let speechRate = 1.0;
    let pauseResolve = null; // for pause/resume
    let currentLang = localStorage.getItem('Therapist_lang') || 'en';
    
    // ─── Persistence state
    let sessionState = { sessionId: null, logs: {} };
    let resumingFrom = null;

    // ─── DOM References ─────────────────────────────────────
    const $ = (id) => document.getElementById(id);

    const dom = {
        app:              document.querySelector('.app'),
        exerciseNum:      $('exercise-num'),
        exerciseTotal:    $('exercise-total'),
        exerciseName:     $('exercise-name'),
        exerciseDesc:     $('exercise-desc'),
        exerciseLabel:    $('exercise-label'),
        countdownNumber:  $('countdown-number'),
        phaseLabel:       $('phase-label'),
        ringProgress:     $('ring-progress'),
        repCurrent:       $('rep-current'),
        repTotal:         $('rep-total'),
        motivationBanner: $('motivation-banner'),
        motivationText:   $('motivation-text'),
        progressFill:     $('progress-fill'),
        progressLabel:    $('progress-label'),
        btnStart:         $('btn-start'),
        btnPause:         $('btn-pause'),
        btnStop:          $('btn-stop'),
        btnSkip:          $('btn-skip'),
        voiceSelect:      $('voice-select'),
        voiceRate:        $('voice-rate'),
        rateValue:        $('rate-value'),
        btnTestVoice:     $('btn-test-voice'),
        exerciseImage:    $('exercise-image'),
        btnLang:          $('btn-lang'),
        langLabel:        $('lang-label'),
        preloader:        $('preloader'),
        preloaderFill:    $('preloader-fill'),
        preloaderSkip:    $('preloader-skip'),
        preloaderStatus:  $('preloader-status'),
        confirmModal:     $('confirm-modal'),
        confirmTitle:     $('confirm-title'),
        confirmDesc:      $('confirm-desc'),
        btnConfirmCancel: $('btn-confirm-cancel'),
        btnConfirmAction: $('btn-confirm-action'),
        btnCloseVoice:    $('btn-close-voice'),
        voiceDetails:     document.querySelector('.voice-settings')
    };


    // ─── Load Exercises ─────────────────────────────────────
    async function loadExercises() {
        const raw = document.getElementById('exercise-data');
        if (!raw) { console.error('No exercise data found'); return; }

        const parsed = JSON.parse(raw.textContent);

        // Handle both QuerySet serialization formats
        if (Array.isArray(parsed)) {
            exercises = parsed.map(item => {
                // If it's a Django model serialized via json_script with template context
                if (item.fields) return { ...item.fields, id: item.pk };
                return item;
            });
        } else if (parsed.exercises) {
            exercises = parsed.exercises;
        }

        // Fallback: if exercises came from template context (model instances),
        // they might be serialized as model repr strings. Use API instead.
        if (exercises.length === 0 || typeof exercises[0] === 'string') {
            await fetchExercisesFromAPI();
            return;
        }

        dom.exerciseTotal.textContent = exercises.length;
        console.log(`[Therapist] Loaded ${exercises.length} exercises`);
    }

    async function fetchExercisesFromAPI() {
        try {
            const resp = await fetch('/api/exercises/');
            const data = await resp.json();
            exercises = data.exercises;
            dom.exerciseTotal.textContent = exercises.length;
            console.log(`[Therapist] Loaded ${exercises.length} exercises from API`);
        } catch (err) {
            console.error('[Therapist] Failed to load exercises:', err);
        }
    }

    // ─── Persistence ─────────────────────────────────────────
    function saveLocalState() {
        if (!isRunning || exercises.length === 0) return;
        const exId = exercises[currentExerciseIdx].id;
        sessionState.logs[exId] = currentRep;
        
        localStorage.setItem('Therapist_state', JSON.stringify({
            exerciseIdx: currentExerciseIdx,
            rep: currentRep,
            sessionState: sessionState
        }));
    }

    async function syncState(status = 'in_progress') {
        if (Object.keys(sessionState.logs).length === 0) return;
        
        const logsArray = Object.keys(sessionState.logs).map(id => ({
            exercise_id: parseInt(id, 10),
            reps_completed: sessionState.logs[id]
        }));
        
        const payload = {
            session_id: sessionState.sessionId,
            status: status,
            logs: logsArray
        };
        
        try {
            const resp = await fetch('/api/sync/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data.session_id) {
                sessionState.sessionId = data.session_id;
                // update local storage with new session ID
                if (isRunning) saveLocalState();
            }
        } catch (err) {
            console.warn('[Therapist] Sync failed. Queuing for offline retry:', err);
            queueOfflineSync(payload);
        }
    }

    function queueOfflineSync(payload) {
        try {
            let queue = JSON.parse(localStorage.getItem('Therapist_offline_queue') || '[]');
            if (payload.session_id) {
                const idx = queue.findIndex(q => q.session_id === payload.session_id);
                if (idx >= 0) queue[idx] = payload;
                else queue.push(payload);
            } else {
                queue.push(payload);
            }
            localStorage.setItem('Therapist_offline_queue', JSON.stringify(queue));
        } catch(e) {
            console.error('Failed to queue offline sync', e);
        }
    }

    async function processOfflineQueue() {
        try {
            let queue = JSON.parse(localStorage.getItem('Therapist_offline_queue') || '[]');
            if (queue.length === 0) return;
            
            console.log(`[Therapist] Processing ${queue.length} offline sync items...`);
            let remaining = [];
            
            for (let payload of queue) {
                try {
                    const resp = await fetch('/api/sync/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (!resp.ok) remaining.push(payload);
                } catch(e) {
                    remaining.push(payload); // still offline
                }
            }
            
            if (remaining.length !== queue.length) {
                localStorage.setItem('Therapist_offline_queue', JSON.stringify(remaining));
            }
        } catch(e) {
            console.error('Failed to process offline queue', e);
        }
    }


    // ─── Global Audio State ─────────────────────────────────
    let ttsManifest = {};
    const CACHE_NAME = 'therapist-audio-v1';
    let globalAudio = new Audio(); // Single element for iOS compatibility

    function stopAudio() {
        globalAudio.pause();
        globalAudio.currentTime = 0;
        window.speechSynthesis.cancel();
    }

    function speakWithWebSpeech(text) {
        return new Promise((resolve) => {
            window.speechSynthesis.cancel();
            
            let isResolved = false;
            let fallbackTimeout;
            
            const handleResolve = () => {
                if (isResolved) return;
                isResolved = true;
                clearTimeout(fallbackTimeout);
                resolve();
            };

            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'en-US';
            if (selectedVoice) utter.voice = selectedVoice;
            utter.rate = speechRate;
            utter.pitch = 1.0;
            utter.volume = 1.0;
            
            // Calculate timeout: ~2 words per sec + 2s buffer, minimum 3s
            const estimatedDurationMs = Math.max(3000, (text.split(' ').length / 2) * 1000 * (1 / speechRate) + 2000);
            
            fallbackTimeout = setTimeout(() => {
                console.warn('[Speech] Web Speech timeout triggered, unblocking:', text);
                window.speechSynthesis.cancel(); // Force clear the stuck utterance
                handleResolve();
            }, estimatedDurationMs);

            utter.onend = handleResolve;
            utter.onerror = (e) => { 
                console.warn('[Speech] Error:', e.error); 
                handleResolve(); 
            };
            
            window.speechSynthesis.speak(utter);
        });
    }

    function playAudioUrl(url) {
        return new Promise((resolve, reject) => {
            stopAudio();
            globalAudio.src = url;
            globalAudio.playbackRate = Math.min(speechRate, 1.3);
            globalAudio.onended = resolve;
            globalAudio.onerror = () => reject(new Error('Audio load failed'));
            globalAudio.play().catch(reject);
        });
    }

    function speakWithGTTS(text) {
        if (!text) return Promise.resolve();
        return new Promise((resolve) => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);
            fetch('/api/tts/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, lang: 'ml' }),
                signal: controller.signal
            })
            .then(resp => {
                clearTimeout(timeoutId);
                if (!resp.ok) throw new Error('TTS API error ' + resp.status);
                return resp.blob();
            })
            .then(blob => {
                const blobUrl = URL.createObjectURL(blob);
                stopAudio();
                globalAudio.src = blobUrl;
                globalAudio.playbackRate = Math.min(speechRate, 1.3);
                globalAudio.onended = () => { URL.revokeObjectURL(blobUrl); resolve(); };
                globalAudio.onerror = () => { URL.revokeObjectURL(blobUrl); resolve(); };
                globalAudio.play().catch(() => resolve());
            })
            .catch(e => {
                clearTimeout(timeoutId);
                console.warn('[gTTS] API failed:', e);
                resolve();
            });
        });
    }

    async function speakWithManifest(text) {
        if (!text || !text.trim()) return;
        const key = `ml_${text}`;
        const url = ttsManifest[key];

        if (url) {
            try {
                await playAudioUrl(url);
                return; // Success — done
            } catch(e) {
                console.warn('[Speech] Manifest URL failed, using API fallback for:', text.substring(0, 30));
            }
        } else {
            console.warn('[Speech] Not in manifest, using API fallback for:', key.substring(0, 40));
        }

        // Fallback: call live TTS API (handles personalized phrases + missing strings)
        return speakWithGTTS(text);
    }

    async function speak(text) {
        if (!text || !text.trim()) return Promise.resolve();
        if (currentLang === 'en') {
            return speakWithWebSpeech(text);
        } else {
            return speakWithManifest(text);
        }
    }

    async function preloadAssets() {
        dom.preloader.classList.remove('preloader--hidden');
        dom.preloaderStatus.textContent = 'Loading Audio Manifest...';
        
        try {
            // Add cache buster to manifest fetch
            const resp = await fetch(`/static/workout/tts_manifest.json?v=${Date.now()}`);
            ttsManifest = await resp.json();
            
            const urls = Object.values(ttsManifest);
            const total = urls.length;
            let loaded = 0;

            dom.preloaderStatus.textContent = 'Caching Audio Files...';
            const cache = await caches.open(CACHE_NAME);
            
            // Fetch in parallel chunks to avoid hanging the browser
            const batchSize = 10;
            for (let i = 0; i < total; i += batchSize) {
                const batch = urls.slice(i, i + batchSize);
                await Promise.all(batch.map(async (url) => {
                    try {
                        const cached = await cache.match(url);
                        if (!cached) {
                            await cache.add(url);
                        }
                    } catch(e) {
                        console.warn("Failed to cache", url);
                    }
                    loaded++;
                }));
                const percent = Math.round((loaded / total) * 100);
                dom.preloaderFill.style.width = `${percent}%`;
            }
            
            dom.preloaderStatus.textContent = 'Ready!';
            setTimeout(() => {
                dom.preloader.classList.add('preloader--hidden');
            }, 500);

        } catch (err) {
            console.error('[Preload] Failed to load manifest', err);
            dom.preloaderStatus.textContent = 'Error loading assets. Please refresh.';
        }
    }

    function populateVoices() {
        const voices = window.speechSynthesis.getVoices();
        dom.voiceSelect.innerHTML = '';

        const langPrefix = currentLang === 'ml' ? 'ml' : 'en';

        // Filter voices by current language
        const langVoices = voices.filter(v =>
            v.lang.startsWith(langPrefix)
        );

        // If we have voices for the current language, only show those
        // Otherwise show all as a fallback
        const voicesToShow = langVoices.length > 0 ? langVoices : voices;

        voicesToShow.forEach((voice, i) => {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `${voice.name} (${voice.lang})`;
            opt.dataset.voiceURI = voice.voiceURI;
            dom.voiceSelect.appendChild(opt);
        });

        // Auto-select best voice: prefer natural/premium voices
        let preferred = null;
        if (currentLang === 'ml') {
            // HIGH PRIORITY: Look for Google or Neural Malayalam
            preferred = voices.find(v => 
                v.lang.startsWith('ml') && /google|neural|natural/i.test(v.name)
            ) || voices.find(v => v.lang.startsWith('ml'));
        } else {
            preferred = voices.find(v =>
                /google.*us|microsoft.*natural|neural|samantha|daniel|karen/i.test(v.name)
            ) || voices.find(v => v.lang.startsWith('en'));
        }

        if (preferred) {
            selectedVoice = preferred;
            // Find its index in voicesToShow
            const idx = voicesToShow.indexOf(preferred);
            if (idx !== -1) {
                dom.voiceSelect.selectedIndex = idx;
            }
        } else {
            // If no voice found for this language, set to null
            // This forces the browser to use its default engine for utter.lang
            selectedVoice = null;
            dom.voiceSelect.selectedIndex = -1;
        }

        console.log(`[Therapist] Voice set for ${currentLang}: ${selectedVoice?.name || 'System Default'}`);
    }

    function updateUIForLanguage() {
        const phase = dom.app.getAttribute('data-phase');
        const isRest = (phase === 'exercise-rest');

        // Update static UI elements
        const exLabelNode = dom.exerciseLabel.childNodes[0];
        const sepNode = dom.exerciseLabel.childNodes[2]; 
        
        if (exLabelNode && exLabelNode.nodeType === 3) {
            exLabelNode.textContent = isRest ? (t('nextUp') + ': ') : (t('exercise') + ' ');
        }
        
        if (sepNode && sepNode.nodeType === 3) {
            sepNode.textContent = isRest ? '' : ' / ';
        }

        dom.langLabel.textContent = currentLang.toUpperCase();
        
        if (exercises.length > 0) {
            dom.exerciseNum.textContent = isRest ? '' : (currentExerciseIdx + 1);
            dom.exerciseTotal.textContent = isRest ? '' : exercises.length;
            
            const ex = exercises[currentExerciseIdx];
            if (ex) {
                dom.exerciseName.textContent = getName(ex);
                dom.exerciseDesc.textContent = getDesc(ex);
                setExerciseImage(ex.order || (currentExerciseIdx + 1));
            }
        }

        // Update idle state text
        if (!isRunning) {
            if (currentExerciseIdx === 0 && currentRep === 0) {
                dom.exerciseName.textContent = t('readyTitle');
                dom.exerciseDesc.textContent = t('readyDesc');
            }
        }
    }

    function switchLanguage() {
        currentLang = currentLang === 'en' ? 'ml' : 'en';
        localStorage.setItem('Therapist_lang', currentLang);
        populateVoices();
        updateUIForLanguage();
    }


    // ─── Wake Lock ──────────────────────────────────────────
    async function acquireWakeLock() {
        if (!('wakeLock' in navigator)) {
            console.warn('[WakeLock] Not supported');
            return;
        }
        try {
            wakeLockSentinel = await navigator.wakeLock.request('screen');
            console.log('[WakeLock] Acquired');

            wakeLockSentinel.addEventListener('release', () => {
                console.log('[WakeLock] Released');
            });
        } catch (err) {
            console.warn('[WakeLock] Failed:', err);
        }
    }

    async function releaseWakeLock() {
        if (wakeLockSentinel) {
            await wakeLockSentinel.release();
            wakeLockSentinel = null;
        }
    }


    // ─── UI Helpers ─────────────────────────────────────────
    function setPhase(phase) {
        dom.app.setAttribute('data-phase', phase);
        const translatedPhase = t('phase_' + phase.replace('-', '_')) || phase.toUpperCase().replace('-', ' ');
        dom.phaseLabel.textContent = translatedPhase;
    }

    function setCountdown(num) {
        dom.countdownNumber.textContent = num;
        // Trigger tick animation
        dom.countdownNumber.classList.remove('tick');
        // Force reflow
        void dom.countdownNumber.offsetWidth;
        dom.countdownNumber.classList.add('tick');
    }

    function setRingProgress(fraction) {
        // fraction: 0 (empty) to 1 (full)
        const offset = CIRCUMFERENCE * (1 - fraction);
        dom.ringProgress.style.strokeDashoffset = offset;
    }

    function updateOverallProgress() {
        const totalExercises = exercises.length;
        if (totalExercises === 0) return;

        const completedExercises = currentExerciseIdx;
        const currentExReps = exercises[currentExerciseIdx]?.reps || 20;
        const repFraction = currentRep / currentExReps;
        const overallFraction = (completedExercises + repFraction) / totalExercises;
        const percent = Math.round(overallFraction * 100);

        dom.progressFill.style.width = `${percent}%`;
        dom.progressLabel.textContent = `${percent}%`;
    }

    function showMotivation(text) {
        dom.motivationText.textContent = text;
        dom.motivationBanner.classList.remove('motivation-banner--hidden');
        dom.motivationBanner.classList.add('motivation-banner--visible');
    }

    function hideMotivation() {
        dom.motivationBanner.classList.remove('motivation-banner--visible');
        dom.motivationBanner.classList.add('motivation-banner--hidden');
    }

    function getMotivationalPhrase(rep) {
        let category = 'phase_a';
        if (rep >= 8 && rep <= 15) category = 'phase_b';
        else if (rep >= 16) category = 'phase_c';

        const phrases = t('motivational')[category];
        const idx = Math.floor(Math.random() * phrases.length);
        return phrases[idx];
    }

    function setExerciseImage(exerciseOrder) {
        if (!dom.exerciseImage) return;
        const base = window.Therapist_IMAGES_BASE || '/static/workout/images/';
        const newSrc = `${base}exercise_${exerciseOrder}.png`;
        dom.exerciseImage.src = newSrc;
        dom.exerciseImage.alt = `Exercise ${exerciseOrder} demonstration`;
    }

    function hideExerciseImage() {
        // No-op in single-viewport layout — image always visible
    }


    // ─── Pause Support ──────────────────────────────────────
    function waitIfPaused() {
        if (!isPaused) return Promise.resolve();
        return new Promise((resolve) => {
            pauseResolve = resolve;
        });
    }

    function checkAborted() {
        if (!isRunning) throw new Error('WORKOUT_STOPPED');
    }


    // ─── Visual-only countdown (for silent rest) ────────────
    function visualCountdown(seconds) {
        return new Promise((resolve) => {
            let remaining = seconds;
            setCountdown(remaining);
            setRingProgress(1);

            const interval = setInterval(async () => {
                // Handle pause
                if (isPaused) {
                    clearInterval(interval);
                    await waitIfPaused();
                    if (!isRunning) { clearInterval(interval); resolve(); return; }
                    // Restart from where we left off
                    const resumed = visualCountdown(remaining);
                    resumed.then(resolve);
                    return;
                }

                if (!isRunning) {
                    clearInterval(interval);
                    resolve();
                    return;
                }

                remaining--;
                if (remaining <= 0) {
                    clearInterval(interval);
                    setCountdown(0);
                    setRingProgress(0);
                    resolve();
                } else {
                    setCountdown(remaining);
                    setRingProgress(remaining / seconds);
                }
            }, 1000);
        });
    }


    // ─── Main Workout Flow ──────────────────────────────────
    async function runWorkout() {
        isRunning = true;
        isPaused = false;
        currentExerciseIdx = 0;
        currentRep = 0;

        // Do not await this: let the wake lock initialize in the background 
        // so the UI immediately updates to "Exercise 1" without a delay.
        acquireWakeLock();

        try {
            for (let exIdx = 0; exIdx < exercises.length; exIdx++) {
                currentExerciseIdx = exIdx;
                const ex = exercises[exIdx];
                const reps = ex.reps || 20;
                const holdSecs = ex.hold_seconds || 10;
                const restSecs = ex.rest_seconds || 5;

                updateUIForLanguage();


                // ── Announce Exercise ──
                checkAborted();
                await waitIfPaused();
                setPhase('announce');
                updateUIForLanguage();
                
                dom.repCurrent.textContent = '0';
                dom.repTotal.textContent = reps;
                setCountdown('');
                setRingProgress(0);
                updateOverallProgress();

                await speak(t('announce')(exIdx + 1, getName(ex), getDesc(ex)));
                checkAborted();
                await waitIfPaused();

                // Brief pause after announcement
                await delay(800);

                // ── Rep Loop ──
                for (let rep = 1; rep <= reps; rep++) {
                    currentRep = rep;
                    saveLocalState();
                    checkAborted();
                    await waitIfPaused();

                    // Motivational phrase every 4 reps (starting from rep 4)
                    let repAnnouncement = `${t('rep')} ${rep}`;
                    let motivationalPhrase = null;
                    if (rep > 1 && rep % 4 === 0) {
                        motivationalPhrase = getMotivationalPhrase(rep);
                        showMotivation(motivationalPhrase);
                    } else if (rep === 1) {
                        hideMotivation();
                    }

                    // Announce rep — speak motivational phrase first, then rep number
                    setPhase('announce');
                    dom.repCurrent.textContent = rep;
                    updateOverallProgress();
                    if (motivationalPhrase) {
                        await speak(motivationalPhrase);
                        checkAborted();
                        await waitIfPaused();
                    }
                    await speak(repAnnouncement);
                    checkAborted();
                    await waitIfPaused();

                    // ── HOLD Phase: speech-driven countdown ──
                    setPhase('hold');
                    await speak(t('hold'));
                    checkAborted();

                    for (let sec = 1; sec <= holdSecs; sec++) {
                        await waitIfPaused();
                        checkAborted();

                        setCountdown(sec);
                        setRingProgress(sec / holdSecs);

                        // Speak the number (fire and forget so it doesn't block the timer)
                        speak(String(sec)).catch(e => console.warn(e));
                        
                        // Wait exactly 1 real second
                        await delay(1000);
                        checkAborted();
                    }

                    // ── REST Phase ──
                    await waitIfPaused();
                    checkAborted();
                    setPhase('rest');

                    if (rep < reps) {
                        await speak(t('relax'));
                        checkAborted();
                        await visualCountdown(restSecs);
                    } else {
                        // Last rep of this exercise
                        await speak(t('exerciseDone'));
                        checkAborted();
                    }

                    hideMotivation();
                }

                // ── Exercise Rest (between exercises) ──
                if (exIdx < exercises.length - 1) {
                    checkAborted();
                    await waitIfPaused();
                    setPhase('exercise-rest');

                    // Update state to next exercise for the UI
                    currentExerciseIdx = exIdx + 1;
                    updateUIForLanguage();

                    const nextEx = exercises[currentExerciseIdx];
                    await speak(t('restNext')(getName(nextEx)));
                    checkAborted();

                    // Sync to server after each exercise completes naturally
                    syncState('in_progress');

                    await visualCountdown(EXERCISE_REST_SECONDS);
                    checkAborted();
                }
            }

            // ── Workout Complete ──
            onWorkoutComplete();

        } catch (err) {
            if (err.message === 'WORKOUT_STOPPED') {
                console.log('[Therapist] Workout stopped by user');
                resetUI();
            } else {
                console.error('[Therapist] Unexpected error:', err);
            }
        } finally {
            isRunning = false;
            isPaused = false;
            stopAudio();
        }
    }

    function delay(ms) {
        return new Promise(r => setTimeout(r, ms));
    }


    // ─── Workout Complete ───────────────────────────────────
    async function onWorkoutComplete() {
        await syncState('completed');
        localStorage.removeItem('Therapist_state');
        sessionState = { sessionId: null, logs: {} };
        
        setPhase('complete');
        setCountdown('!');
        dom.phaseLabel.textContent = 'DONE';
        dom.progressFill.style.width = '100%';
        dom.progressLabel.textContent = '100%';

        speak(t('workoutComplete'));
        window.dispatchEvent(new CustomEvent('Therapist_workout_complete'));

        // Show completion overlay
        const overlay = document.createElement('div');
        overlay.className = 'completion-overlay';
        overlay.innerHTML = `
            <div class="completion-overlay__icon">&#127942;</div>
            <h2 class="completion-overlay__title">Workout Complete!</h2>
            <p class="completion-overlay__subtitle">All ${exercises.length} exercises finished. Outstanding work!</p>
            <button class="completion-overlay__btn" onclick="this.closest('.completion-overlay').remove()">Done</button>
        `;
        document.body.appendChild(overlay);

        releaseWakeLock();
        resetControls();
    }


    // ─── UI Reset ───────────────────────────────────────────
    function resetUI() {
        setPhase('idle');
        dom.exerciseName.textContent = t('readyTitle');
        dom.exerciseDesc.textContent = t('readyDesc');
        dom.exerciseNum.textContent = '-';
        dom.repCurrent.textContent = '0';
        dom.countdownNumber.textContent = '0';
        dom.phaseLabel.textContent = t('phase_idle') || 'IDLE';
        setRingProgress(0);
        dom.progressFill.style.width = '0%';
        dom.progressLabel.textContent = '0%';
        hideMotivation();
        setExerciseImage(1);
        releaseWakeLock();
        resetControls();
    }

    function resetControls() {
        dom.btnStart.style.display = '';
        dom.btnPause.style.display = 'none';
        dom.btnStart.disabled = false;
        dom.btnStop.disabled = true;
        dom.btnSkip.disabled = true;
    }


    // ─── Control Handlers ───────────────────────────────────
    function onStart() {
        // Unlock global audio on first interaction for iOS Safari
        globalAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA'; // Silent WAV
        globalAudio.play().catch(e => {});

        if (isRunning && isPaused) {
            // Resume
            isPaused = false;
            dom.btnPause.style.display = '';
            dom.btnStart.style.display = 'none';
            if (pauseResolve) {
                pauseResolve();
                pauseResolve = null;
            }
            return;
        }

        dom.btnStart.style.display = 'none';
        dom.btnPause.style.display = '';
        dom.btnPause.disabled = false;
        dom.btnStop.disabled = false;
        dom.btnSkip.disabled = false;

        if (resumingFrom) {
            runWorkoutFrom(resumingFrom.exerciseIdx, resumingFrom.rep);
            resumingFrom = null;
        } else {
            // New session, sync start
            sessionState = { sessionId: null, logs: {} };
            runWorkout();
        }
    }

    function onPause() {
        if (!isRunning) return;
        isPaused = true;
        stopAudio();

        dom.btnPause.style.display = 'none';
        dom.btnStart.style.display = '';
        // Start button now acts as Resume
    }

    function showConfirm(title, desc, confirmText, isDanger = true) {
        return new Promise((resolve) => {
            dom.confirmTitle.textContent = title;
            dom.confirmDesc.textContent = desc;
            dom.btnConfirmAction.textContent = confirmText;
            
            if (isDanger) {
                dom.btnConfirmAction.className = 'confirm-btn confirm-btn--danger';
            } else {
                dom.btnConfirmAction.className = 'confirm-btn confirm-btn--primary'; // skip button style
            }

            dom.confirmModal.classList.remove('confirm-modal--hidden');

            const cleanup = () => {
                dom.btnConfirmCancel.removeEventListener('click', onCancel);
                dom.btnConfirmAction.removeEventListener('click', onConfirm);
                dom.confirmModal.classList.add('confirm-modal--hidden');
            };

            const onCancel = () => { cleanup(); resolve(false); };
            const onConfirm = () => { cleanup(); resolve(true); };

            dom.btnConfirmCancel.addEventListener('click', onCancel);
            dom.btnConfirmAction.addEventListener('click', onConfirm);
        });
    }

    async function onStop() {
        // Flush current exercise reps into logs BEFORE setting isRunning=false
        // so syncState has the latest data to send to the server
        if (isRunning && exercises.length > 0) {
            const exId = exercises[currentExerciseIdx].id;
            if (currentRep > 0) {
                sessionState.logs[exId] = currentRep;
            }
        }

        isRunning = false;
        isPaused = false;
        stopAudio();
        if (pauseResolve) {
            pauseResolve();
            pauseResolve = null;
        }

        // Await sync so the session is saved before we clear state
        await syncState('abandoned');
        localStorage.removeItem('Therapist_state');
        sessionState = { sessionId: null, logs: {} };
        resetUI();
    }

    function onSkip() {
        if (!isRunning || currentExerciseIdx >= exercises.length - 1) return;

        const nextIdx = currentExerciseIdx + 1;

        // Flush current reps BEFORE setting isRunning=false
        if (exercises.length > 0 && currentRep > 0) {
            const exId = exercises[currentExerciseIdx].id;
            sessionState.logs[exId] = currentRep;
        }

        isRunning = false;
        isPaused = false;
        stopAudio();
        if (pauseResolve) { pauseResolve(); pauseResolve = null; }

        // Small delay then restart from next exercise
        setTimeout(() => {
            syncState('in_progress');
            
            currentExerciseIdx = nextIdx;
            currentRep = 0;
            isRunning = true;
            runWorkoutFrom(nextIdx, 1);
        }, 300);
    }

    async function runWorkoutFrom(startIdx, startRep = 1) {
        isRunning = true;
        isPaused = false;

        dom.btnStart.style.display = 'none';
        dom.btnPause.style.display = '';
        dom.btnPause.disabled = false;
        dom.btnStop.disabled = false;
        dom.btnSkip.disabled = false;

        // Do not await this to prevent UI freezing on skip
        acquireWakeLock();

        try {
            for (let exIdx = startIdx; exIdx < exercises.length; exIdx++) {
                currentExerciseIdx = exIdx;
                const ex = exercises[exIdx];
                const reps = ex.reps || 20;
                const holdSecs = ex.hold_seconds || 10;
                const restSecs = ex.rest_seconds || 5;

                checkAborted();
                await waitIfPaused();
                setPhase('announce');
                dom.exerciseNum.textContent = exIdx + 1;
                dom.exerciseName.textContent = getName(ex);
                dom.exerciseDesc.textContent = getDesc(ex);
                dom.repCurrent.textContent = '0';
                dom.repTotal.textContent = reps;
                setCountdown('');
                setRingProgress(0);
                setExerciseImage(ex.order || (exIdx + 1));
                updateOverallProgress();

                await speak(t('announce')(exIdx + 1, getName(ex), getDesc(ex)));
                checkAborted();
                await waitIfPaused();
                
                // If resuming mid-exercise, we skip the 800ms delay and jump into the rep loop
                if (startRep === 1) {
                    await delay(800);
                }

                for (let rep = startRep; rep <= reps; rep++) {
                    currentRep = rep;
                    saveLocalState();
                    checkAborted();
                    await waitIfPaused();

                    let repAnnouncement = `${t('rep')} ${rep}`;
                    let motivationalPhrase = null;
                    if (rep > 1 && rep % 4 === 0) {
                        motivationalPhrase = getMotivationalPhrase(rep);
                        showMotivation(motivationalPhrase);
                    } else if (rep === 1) {
                        hideMotivation();
                    }

                    setPhase('announce');
                    dom.repCurrent.textContent = rep;
                    updateOverallProgress();
                    if (motivationalPhrase) {
                        await speak(motivationalPhrase);
                        checkAborted();
                        await waitIfPaused();
                    }
                    await speak(repAnnouncement);
                    checkAborted();
                    await waitIfPaused();

                    setPhase('hold');
                    await speak(t('hold'));
                    checkAborted();

                    for (let sec = 1; sec <= holdSecs; sec++) {
                        await waitIfPaused();
                        checkAborted();
                        setCountdown(sec);
                        setRingProgress(sec / holdSecs);
                        await speak(String(sec));
                        checkAborted();
                    }

                    await waitIfPaused();
                    checkAborted();
                    setPhase('rest');

                    if (rep < reps) {
                        await speak(t('relax'));
                        checkAborted();
                        await visualCountdown(restSecs);
                    } else {
                        await speak(t('exerciseDone'));
                        checkAborted();
                    }

                    hideMotivation();
                }

                // Reset startRep to 1 so that the NEXT exercise in the loop starts from the beginning
                startRep = 1;

                if (exIdx < exercises.length - 1) {
                    checkAborted();
                    await waitIfPaused();
                    setPhase('exercise-rest');

                    // Show next exercise details during rest
                    currentExerciseIdx = exIdx + 1;
                    updateUIForLanguage();

                    const nextEx = exercises[currentExerciseIdx];
                    await speak(t('restNext')(getName(nextEx)));
                    checkAborted();
                    
                    syncState('in_progress');
                    
                    await visualCountdown(EXERCISE_REST_SECONDS);
                    checkAborted();
                }
            }

            onWorkoutComplete();

        } catch (err) {
            if (err.message === 'WORKOUT_STOPPED') {
                console.log('[Therapist] Workout stopped by user');
                resetUI();
            } else {
                console.error('[Therapist] Error:', err);
            }
        } finally {
            isRunning = false;
            isPaused = false;
            stopAudio();
        }
    }


    // ─── Initialization ─────────────────────────────────────
    async function init() {
        await loadExercises();
        
        // Check for saved state
        try {
            const saved = localStorage.getItem('Therapist_state');
            if (saved) {
                const state = JSON.parse(saved);
                if (state.sessionState) {
                    sessionState = state.sessionState;
                    resumingFrom = {
                        exerciseIdx: state.exerciseIdx,
                        rep: state.rep
                    };
                    
                    // Update UI to show resume status
                    const ex = exercises[state.exerciseIdx];
                    if (ex) {
                        dom.exerciseName.textContent = `Resume: ${getName(ex)}`;
                        dom.exerciseDesc.textContent = `You left off at rep ${state.rep}. Press Start to continue.`;
                        dom.btnStart.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><polygon points="6,4 20,12 6,20"/></svg>';
                        dom.btnStart.title = "Resume Workout";
                    }
                }
            }
        } catch (e) {
            console.warn('[Therapist] Failed to load saved state');
        }

        updateUIForLanguage();
        dom.btnLang.addEventListener('click', switchLanguage);

        await preloadAssets();
        processOfflineQueue();
        // Voice setup
        if ('speechSynthesis' in window) {
            // Voices may load async
            speechSynthesis.onvoiceschanged = populateVoices;
            populateVoices(); // Try immediately too
        }

        // Voice selection change
        dom.voiceSelect.addEventListener('change', () => {
            const voices = window.speechSynthesis.getVoices();
            const langPrefix = currentLang === 'ml' ? 'ml' : 'en';
            const langVoices = voices.filter(v => v.lang.startsWith(langPrefix));
            const voicesToShow = langVoices.length > 0 ? langVoices : voices;
            const idx = parseInt(dom.voiceSelect.value, 10);
            selectedVoice = voicesToShow[idx] || null;
        });

        // Rate slider
        dom.voiceRate.addEventListener('input', () => {
            speechRate = parseFloat(dom.voiceRate.value);
            dom.rateValue.textContent = speechRate.toFixed(2);
        });

        // Test voice button
        dom.btnTestVoice.addEventListener('click', () => {
            speak(t('testVoice'));
        });

        dom.btnCloseVoice.addEventListener('click', () => {
            dom.voiceDetails.open = false;
        });

        // Control buttons
        dom.btnStart.addEventListener('click', onStart);
        dom.btnPause.addEventListener('click', onPause);
        dom.btnStop.addEventListener('click', async () => {
            const confirmed = await showConfirm('Stop Workout?', 'Are you sure you want to end this session completely?', 'Stop', true);
            if (confirmed) onStop();
        });
        dom.btnSkip.addEventListener('click', async () => {
            const confirmed = await showConfirm('Skip Exercise?', 'Are you sure you want to skip to the next exercise?', 'Skip', false);
            if (confirmed) onSkip();
        });

        // Re-acquire wake lock on visibility change (browser may release it)
        document.addEventListener('visibilitychange', async () => {
            if (document.visibilityState === 'visible' && isRunning && wakeLockSentinel === null) {
                await acquireWakeLock();
            }
        });

        // (Removed the periodic pause/resume nudge as it causes freezes on Android Chrome during active speech)

        console.log('[Therapist] Player initialized');
    }

    // Boot
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
