import db
import joblib
import os

# Load Model (Lazy Loading)
model = None
try:
    if os.path.exists("text_model.pkl"):
        model = joblib.load("text_model.pkl")
except Exception as e:
    print(f"Error loading model: {e}")

def get_simple_explanation(text):
    """
    Returns a simple, educational explanation for why a text is suspicious.
    Target Audience: Ages 8-80.
    """
    text_lower = text.lower()
    
    # Rule-based explanations
    if any(x in text_lower for x in ["western union", "gift card", "wire transfer"]):
        return "⚠️ **Money Danger**: A stranger is asking you to send money. Real companies never ask for gift cards or wire transfers."
    
    if any(x in text_lower for x in ["password", "verify", "login", "account is locked"]):
        return "🛑 **Account Risk**: Someone is trying to steal your password. Never click links that ask you to log in."
        
    if any(x in text_lower for x in ["urgent", "immediately", "warrant", "jail", "suspended"]):
        return "⏳ **Panic Trick**: Scammers use scary words like 'Urgent' or 'Jail' to make you act without thinking. Take a deep breath."
        
    if any(x in text_lower for x in ["soulmate", "destiny", "love you", "my love"]):
        return "💔 **Romance Scam**: Be careful when someone you met online asks for money. Real love doesn't cost $500."
        
    if any(x in text_lower for x in ["investment", "returns", "profit", "fund"]):
        return "💰 **Too Good To Be True**: If they promise you'll get rich quick, it's a lie. Keep your money safe."
        
    if any(x in text_lower for x in ["security patch", "microsoft", "admin access", "virus"]):
        return "💻 **Fake Support**: Microsoft will never call or email you to fix your computer. Do not let them control your screen."

    return None

def analyze_text(text, context=None):
    """
    Analyzes text using the trained ML model.
    Context: dict with keys like 'is_saved_contact' (bool)
    """
    global model
    
    # Default context
    if context is None:
        context = {}
    
    is_saved = context.get('is_saved_contact', False)
    
    # 1. ML Prediction (if model exists)
    if model:
        try:
            # Get probability of scam (class 1)
            # Assuming model.classes_ is ['safe', 'scam'] or similar. 
            # We find the index of 'scam' dynamically to be safe.
            scam_idx = list(model.classes_).index('scam')
            probability = model.predict_proba([text])[0][scam_idx]
            confidence = int(probability * 100)
            
            # Threshold logic
            # Default strict threshold for unknown numbers
            threshold = 0.4 
            
            if is_saved:
                # Relaxed threshold for saved contacts to avoid false positives
                # Only flag if very high confidence
                threshold = 0.85
            
            if probability > threshold:
                # GENERATE SIMPLE EXPLANATION
                reason = get_simple_explanation(text)
                
                # If no specific rule matched, be careful about flagging generic text
                if reason is None:
                    # Only flag if it's not a short greeting (heuristic)
                    if len(text.split()) > 3:
                        reason = "🤖 **AI Warning**: This message has patterns seen in scams. Proceed with caution."
                        db.log_alert("SMS/Text", "Low", reason, "Flagged")
                        return {"is_scam": True, "reason": reason, "confidence": confidence}
                    else:
                        # It's likely a false positive on a short string like "Hello"
                        return {"is_scam": False, "reason": "✅ **Safe**: Looks like a normal greeting.", "confidence": 90}
                
                db.log_alert("SMS/Text", "High", reason, "Quarantined")
                return {"is_scam": True, "reason": reason, "confidence": confidence}
        except Exception as e:
            print(f"Model prediction error: {e}")

    # 2. Fallback: Keyword Detection
    scam_keywords = [
        "urgent", "bank", "verify", "password", "ssn", "gift card", "compromised", "jail", "warrant", 
        "western union", "visa fee", "soulmate", "destiny", "flight delayed", "investment", "returns", 
        "ticker", "security patch", "admin access", "support line", "microsoft", "diagnostic tool",
        "otp", "cvv", "lottery", "prize", "click here", "winner", "cash", "refund", "blocked", 
        "suspended", "kyc", "pan card", "aadhar", "sim card", "electricity", "ransom", "arrest",
        "transfer", "upi", "gpay", "paytm", "lost phone", "new number"
    ]
    
    # If saved contact, only check for very specific high-danger keywords if ML failed or didn't run
    if is_saved:
        # Reduced list for saved contacts
        scam_keywords = ["password", "ssn", "cvv", "otp"]

    text_lower = text.lower()
    for word in scam_keywords:
        if word in text_lower:
            # GENERATE SIMPLE EXPLANATION
            reason = get_simple_explanation(text)
            if reason is None:
                reason = f"⚠️ **Keyword Alert**: Contains suspicious word '{word}'."
            
            db.log_alert("SMS/Text", "Medium", reason, "Quarantined")
            return {
                "is_scam": True,
                "reason": reason,
                "confidence": 85
            }
            
    return {"is_scam": False, "reason": "✅ **Safe**: This message looks like a normal conversation.", "confidence": 95}

import speech_recognition as sr
from deep_translator import GoogleTranslator

# Initialize Translator (Not needed as object for deep_translator usually, but we can wrap it or just use it directly)

def process_audio_input(audio_file, language_code):
    """
    Transcribes audio and translates to English.
    Handles low-quality audio and background noise.
    """
    r = sr.Recognizer()
    
    # Settings for low-quality audio
    r.energy_threshold = 300  # Lower threshold for quiet voices
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    
    try:
        # Load audio file
        with sr.AudioFile(audio_file) as source:
            # Calibrate for background noise (crucial for bad mics)
            print("Calibrating for noise...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source)
            
        # Transcribe
        # Map UI languages to Google Speech API codes
        lang_map = {
            "English": "en-US",
            "Hindi": "hi-IN",
            "Marathi": "mr-IN"
        }
        api_lang = lang_map.get(language_code, "en-US")
        
        print(f"Transcribing in {api_lang}...")
        # show_all=False returns just the text
        text = r.recognize_google(audio_data, language=api_lang)
        print(f"Original Text: {text}")
        
        # Translate if not English
        if language_code != "English":
            print("Translating to English...")
            english_text = GoogleTranslator(source='auto', target='en').translate(text)
            print(f"Translated: {english_text}")
            return text, english_text
        
        return text, text
        
    except sr.UnknownValueError:
        return None, "Could not understand audio. Please speak clearly."
    except sr.RequestError as e:
        return None, f"Speech API Error (Check Internet): {e}"
    except ValueError as e:
        return None, f"Audio Format Error: {e}"
    except Exception as e:
        return None, f"Error: {e}"

def analyze_audio(audio_file, language="English", context=None):
    """
    Analyzes audio for deepfakes AND content scams.
    """
    # 1. Content Analysis (STT + Text Model)
    # If audio_file is a path or file-like object we can process
    original_text, english_text = process_audio_input(audio_file, language)
    
    content_result = {"is_scam": False, "reason": "Content seems safe"}
    
    if original_text and "Error" not in english_text:
        # Run the text analysis on the transcribed/translated text
        content_result = analyze_text(english_text, context=context)
        content_result["transcript"] = original_text
        content_result["translation"] = english_text

    # 2. Deepfake Analysis (Mock for now, but linked to content)
    # In a real app, this would check spectral features.
    # For prototype, we'll assume high confidence if content is scammy.
    
    is_deepfake = False
    deepfake_confidence = 10
    
    if content_result["is_scam"]:
        is_deepfake = True
        deepfake_confidence = 88
        reason = f"Scam Content Detected in Audio: {content_result['reason']}"
    else:
        reason = "Audio seems natural."

    # Log to DB
    if is_deepfake:
        db.log_alert("Audio Call", "High", reason, "Blocked")

    return {
        "is_scam": is_deepfake,
        "reason": reason,
        "confidence": deepfake_confidence,
        "content_analysis": content_result
    }
