import os
import hashlib
import json
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehabloop.settings')
django.setup()

from workout.models import Exercise
from django.conf import settings

def get_hash(lang, text):
    return hashlib.md5(f"{lang}_{text}".encode('utf-8')).hexdigest() + ".mp3"

def main():
    manifest = {}
    exercises = list(Exercise.objects.all())
    
    # User might not have a USER_NAME set on the backend when generating, 
    # but the frontend replaces `{name}`.
    # Actually, the audio generated in `generate_all_audio.py` did NOT use USER_NAME,
    # it used the hardcoded strings. Let's replicate EXACTLY what was generated.
    
    # Wait, `generate_all_audio.py` generated files using the exact text strings!
    # Let's import the exact strings from the file.
    
    common_strings = {
        'en': {
            'exercise': 'Exercise', 'rep': 'Rep', 'hold': 'Hold', 'relax': 'Relax',
            'exerciseDone': 'And relax. Great job on that set.',
            'workoutComplete': "Amazing work! You have finished the entire routine for today. Your knee is getting stronger every day! Be proud!",
            'testVoice': "Hello! I am your Therapist coach. I will be guiding you step-by-step through today's exercises. Let's get started!",
            'phase_hold': 'HOLD', 'phase_relax': 'RELAX', 'phase_rest': 'REST',
        },
        'ml': {
            'exercise': 'വ്യായാമം', 'rep': 'റെപ്', 'hold': 'പിടിക്കൂ', 'relax': 'ആശ്വസിക്കൂ',
            'exerciseDone': 'ആശ്വസിക്കൂ. ഈ വ്യായാമം വളരെ നന്നായി ചെയ്തു.',
            'workoutComplete': "ഗംഭീരം! ഇന്നത്തെ വ്യായാമങ്ങൾ എല്ലാം നമ്മൾ വിജയകരമായി പൂർത്തിയാക്കിയിരിക്കുന്നു. നിങ്ങളുടെ മുട്ടിന്റെ ആരോഗ്യം മെച്ചപ്പെട്ടുകൊണ്ടിരിക്കുകയാണ് കേട്ടോ!",
            'testVoice': "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ സ്വന്തം ഫിസിയോ കോച്ച് ആണ്. ഇന്നത്തെ വ്യായാമങ്ങൾ നമുക്ക് ഒരുമിച്ച് ചെയ്യാം. റെഡി അല്ലേ?",
            'phase_hold': 'പിടിക്കൂ', 'phase_relax': 'വിശ്രമിക്കൂ', 'phase_rest': 'വിശ്രമിക്കാം',
        }
    }

    motivational_en = [
        "Keep breathing, smooth and steady.", "You are doing great, don't rush it.",
        "Focus on the movement, not the count.", "Your form is perfect right now.",
        "Don't hold your breath, keep the oxygen flowing.", "Keep the knee stable. You are doing great.",
        "Breathe deeply, let the oxygen fuel your muscles.", "Feel that stretch? That is exactly what we want.",
        "Beautiful form! Let's keep that going.", "Take it one second at a time. No rush.",
        "Keep your body aligned and straight.", "Every second of this hold is building stability.",
        "Breathe in gently, breathe out slowly.", "Smooth movements, don't jerk the knee.",
        "Great start! Keep this exact rhythm.", "You have incredible focus today.",
        "Look at that form. Excellent work.", "Nice posture. Keep it steady.",
        "You are doing this perfectly.", "Feel the burn? That is your knee getting stronger.",
        "Excellent control. Keep it up.", "I know it is tough, but you are doing exactly what you need to do.",
        "Every single rep is a step towards full recovery.", "You are doing this for yourself. Keep going.",
        "Almost halfway, keep pushing!", "That is it, exactly like that.",
        "Consistency is the key to recovery, and you are nailing it.", "Every small movement is a big victory for your knee.",
        "You are on the right track. Don't stop now.", "The discomfort means the muscles are waking up.",
        "We are halfway through this exercise, don't quit.", "Your joints are getting the support they need.",
        "If you feel tired, take a deeper breath.", "You are moving forward beautifully.",
        "I am so proud of your consistency.", "I see that effort. Keep it up!",
        "Your progress is truly inspiring.", "Keep that energy up.",
        "I know it burns, but you are doing great.", "You are incredibly resilient.",
        "I am right here with you. Let us finish strong.", "This is where the magic happens, keep working.",
        "Your body is healing, trust the process.", "A little effort today brings a lot of relief tomorrow.",
        "Don't let the fatigue win. You are stronger.", "That is perfect execution. Well done.",
        "Your muscles are adapting and getting stronger.", "You are proving to yourself how tough you are.",
        "Recovery takes patience, and you are doing brilliantly.", "Just a handful left! Let's make them count.",
        "The last few are always the most important.", "Your knee is getting its strength back, almost done!",
        "We are going to complete this set successfully!", "Perfect! You'll get to relax in just a moment.",
        "Stay strong. We are almost done with this set.", "You've got this. Don't give up now!",
        "Let's finish this set together.", "You are doing something amazing for your body today.",
        "You are crushing this workout!", "Finish strong! I'm right here with you.", "Push through these last few!"
    ]
    
    motivational_ml = [
        "നന്നായി ചെയ്യുന്നുണ്ട്, ധൃതി വെക്കണ്ട പതുക്കെ മതി.", "വളരെ നല്ല ഫോം ആണ്, ഇതേപോലെ തന്നെ ചെയ്യാം.",
        "ശ്വാസം നന്നായി എടുത്ത് വിടണം കേട്ടോ, പിടിച്ചു വെക്കരുത്.", "ആ ശ്രദ്ധ അങ്ങനെ തന്നെ നിൽക്കട്ടെ, വളരെ നല്ലത്.",
        "മുട്ട് അനങ്ങാതെ സൂക്ഷിക്കണം കേട്ടോ. നന്നായി ചെയ്യുന്നുണ്ട്.", "പതുക്കെ മതി, ഒട്ടും ധൃതി വെക്കേണ്ട.",
        "നന്നായി ശ്വാസമെടുക്കൂ, പേശികൾക്ക് അത് നല്ലതാണ്.", "ആ വലിഞ്ഞുമുറുകൽ തോന്നുന്നുണ്ടോ? അത് വളരെ നല്ലതാണ്.",
        "വളരെ കൃത്യമായിട്ടാണ് ചെയ്യുന്നത്. വളരെ നല്ലത്.", "അടിപൊളി! ഇങ്ങനെ തന്നെ തുടരാം.",
        "ശരീരം നേരെ വെക്കാൻ പ്രത്യേകം ശ്രദ്ധിക്കുക.", "ഓരോ സെക്കൻഡും പ്രധാനമാണ്, കൃത്യമായി ചെയ്യുക.",
        "ശ്വാസം ഉള്ളിലേക്ക് എടുത്ത് പതിയെ പുറത്തേക്ക് വിടുക.", "മുട്ടിന് അധികം സ്ട്രെസ് കൊടുക്കരുത്, സ്മൂത്ത് ആയി ചെയ്യാം.",
        "തുടക്കം ഗംഭീരമായിട്ടുണ്ട്! ഇതേ രീതിയിൽ തുടരാം.", "വളരെ നന്നായി ചെയ്യുന്നുണ്ട് കേട്ടോ.",
        "നിങ്ങൾ ഇന്ന് വളരെ ഉഷാറാണല്ലോ!", "വളരെ നല്ല പോസ്ചർ ആണ് കേട്ടോ.",
        "ഇങ്ങനെ തന്നെ മതി, ഉഷാറായിട്ടുണ്ട്.", "മുട്ടിന് നല്ല ആശ്വാസം കിട്ടും, കുറച്ചുകൂടി.",
        "വേദനയുണ്ടോ? പേടിക്കണ്ട, ഇത് മാറും.", "ഓരോ തവണ ചെയ്യുമ്പോഴും മുട്ടിന്റെ ബലം കൂടുകയാണ്.",
        "ബുദ്ധിമുട്ടാണെന്ന് എനിക്കറിയാം, പക്ഷെ നന്നായി ചെയ്യുന്നുണ്ട്.", "ഇത് നിങ്ങൾ നിങ്ങൾക്ക് വേണ്ടി ചെയ്യുന്നതാണ്, നിർത്തരുത്.",
        "പകുതി കഴിഞ്ഞു, ഇനി കുറച്ചുകൂടി മാത്രം.", "ഇങ്ങനെ തന്നെ മതി, വളരെ കറക്റ്റ് ആണ്.",
        "തുടർച്ചയായുള്ള ഈ പരിശ്രമമാണ് പെട്ടെന്ന് സുഖം തരിക.", "ഓരോ ചെറിയ ചലനവും വലിയൊരു മാറ്റത്തിലേക്കാണ്.",
        "നിങ്ങൾ ശരിയായ വഴിയിലാണ്. ഇനി നിർത്തരുത്.", "ഇപ്പോൾ കുറച്ചു വേദന തോന്നും, പക്ഷെ അത് പേശികൾ ഉണരുന്നതിന്റെ ലക്ഷണമാണ്.",
        "പകുതി ദൂരം നമ്മൾ പിന്നിട്ടു, ഇനി വിട്ടുകൊടുക്കരുത്.", "നിങ്ങളുടെ കാൽമുട്ടിന് ഇപ്പോൾ നല്ല ഉറപ്പ് കിട്ടുന്നുണ്ട്.",
        "ക്ഷീണം തോന്നുണ്ടെങ്കിൽ ദീർഘമായി ഒന്ന് ശ്വാസമെടുക്കൂ.", "വളരെ നന്നായിട്ട് മുന്നോട്ട് പോകുന്നുണ്ട്.",
        "നിങ്ങളുടെ ഈ പരിശ്രമം ഞാൻ കാണുന്നുണ്ട്. വളരെ നല്ലത്!", "നിങ്ങളുടെ മാറ്റം ശരിക്കും അത്ഭുതപ്പെടുത്തുന്നതാണ് കേട്ടോ.",
        "ഇത്രയും ചെയ്തത് വലിയ കാര്യമാണ്, ഇനി കുറച്ചുകൂടി.", "ആ എനർജി അങ്ങനെ തന്നെ നിൽക്കട്ടെ.",
        "കുറച്ചു ബുദ്ധിമുട്ടുണ്ടാകും, പക്ഷെ വിടരുത്.", "നിങ്ങളുടെ ഈ പരിശ്രമം തീർച്ചയായും ഫലം തരും.",
        "ഞാൻ കൂടെത്തന്നെയുണ്ട്, നമുക്കിത് ഒരുമിച്ച് തീർക്കാം.", "ഇപ്പോഴാണ് പേശികൾക്ക് ശരിക്കും വ്യായാമം കിട്ടുന്നത്, തുടരുക.",
        "ക്ഷീണിച്ചോ? സാരമില്ല, കുറച്ചു കൂടി കഴിഞ്ഞാൽ വിശ്രമിക്കാം.", "ശരീരം പതുക്കെ ഭേദമായി വരികയാണ്, ഈ മാറ്റം വിശ്വസിക്കൂ.",
        "ഇന്നത്തെ ചെറിയൊരു കഷ്ടപ്പാട് നാളത്തെ വലിയൊരു ആശ്വാസമാണ്.", "ക്ഷീണം തോന്നിയാലും വിട്ടുകൊടുക്കരുത്, നിങ്ങൾക്കതിന് സാധിക്കും.",
        "പേശികൾക്ക് പതുക്കെ ബലം വെച്ച് വരികയാണ്.", "നിങ്ങൾക്ക് എത്രത്തോളം ചെയ്യാൻ കഴിയുമെന്ന് നിങ്ങൾ തന്നെ തെളിയിക്കുകയാണ്.",
        "കുറച്ചു ക്ഷമയൊക്കെ വേണ്ടിവരും, പക്ഷെ നിങ്ങൾ നന്നായി ചെയ്യുന്നുണ്ട്.", "ഇനി വിരലിലെണ്ണാവുന്നവ മാത്രം! പവർ വരട്ടെ!",
        "അവസാനത്തെ കുറച്ചെണ്ണം എപ്പോഴും സ്പെഷ്യൽ ആണ്, പൊളിക്കാം!", "മുട്ടിന്റെ പഴയ പവർ തിരിച്ചു വരികയാണ്, തീരാറായി!",
        "ഈ സെറ്റ് നമ്മൾ വിജയകരമായി പൂർത്തിയാക്കാൻ പോകുന്നു!", "പെർഫെക്റ്റ്! ഇനി ഒന്ന് റിലാക്സ് ചെയ്യാൻ സമയമായി.",
        "നിങ്ങളുടെ ഈ നിശ്ചയദാർഢ്യം സമ്മതിക്കണം.", "വിടരുത്, നമുക്കിത് മുഴുവനാക്കണം.",
        "നിങ്ങൾ വളരെ മികച്ച രീതിയിലാണ് ചെയ്യുന്നത്!", "ശരീരത്തിന് വേണ്ടി വളരെ നല്ലൊരു കാര്യമാണ് ഇന്ന് ചെയ്യുന്നത്.",
        "നമുക്കീ സെറ്റ് ഒരുമിച്ച് തീർക്കാം കേട്ടോ.", "അവസാനത്തെ കുറച്ചെണ്ണം നമുക്ക് പവറിൽ തീർക്കാം!",
        "ഗംഭീരം! ഇനി കുറച്ചുകൂടി മാത്രം!"
    ]

    def add_to_manifest(lang, text):
        if text:
            manifest[f"{lang}_{text}"] = "/media/tts_cache/" + get_hash(lang, text)

    for i in range(1, 21):
        add_to_manifest('en', str(i))
        add_to_manifest('ml', str(i))

    for lang in ['en', 'ml']:
        for key, text in common_strings[lang].items():
            add_to_manifest(lang, text)

    for i, ex in enumerate(exercises):
        num = i + 1
        add_to_manifest('en', f"Exercise {num}. {ex.name}. {ex.description or ''}")
        if i < len(exercises) - 1:
            add_to_manifest('en', f"Take a deep breath and rest for a minute. Next up: {exercises[i+1].name}.")
        
        add_to_manifest('ml', f"വ്യായാമം {num}. {ex.name_ml or ex.name}. {ex.description_ml or ''}")
        if i < len(exercises) - 1:
            next_name_ml = exercises[i+1].name_ml or exercises[i+1].name
            add_to_manifest('ml', f"നന്നായി ചെയ്തു. ഇനി ഒരു മിനിറ്റ് വിശ്രമിക്കാം കേട്ടോ. അടുത്തത്: {next_name_ml}.")

    for text in motivational_en:
        add_to_manifest('en', text)
    for text in motivational_ml:
        add_to_manifest('ml', text)

    # Save manifest
    manifest_path = os.path.join(settings.BASE_DIR, 'workout', 'static', 'workout', 'tts_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Manifest written to {manifest_path} with {len(manifest)} entries.")

if __name__ == "__main__":
    main()
