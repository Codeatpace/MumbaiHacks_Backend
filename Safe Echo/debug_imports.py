
try:
    import streamlit
    print("streamlit imported")
except Exception as e:
    print(f"streamlit failed: {e}")

try:
    import firebase_admin
    print("firebase_admin imported")
except Exception as e:
    print(f"firebase_admin failed: {e}")

try:
    import googletrans
    print("googletrans imported")
except Exception as e:
    print(f"googletrans failed: {e}")

try:
    import speech_recognition
    print("speech_recognition imported")
except Exception as e:
    print(f"speech_recognition failed: {e}")
