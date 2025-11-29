import streamlit as st
import guardian
import db

# Page Config
st.set_page_config(
    page_title="SafeEcho",
    page_icon="🛡️",
    layout="centered"
)

def main():
    st.title("🛡️ SafeEcho")
    st.caption("Your Autonomous Digital Guardian")

    # Custom CSS for Mobile Look
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .main-container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-height: 800px;
            color: #333333; /* Force dark text */
        }
        /* Fix for metrics and headers in dark mode if it leaks through */
        h1, h2, h3, p, div {
            color: #333333;
        }
        .stButton button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Always-on Status Bar
    st.markdown("""
        <div style="background-color: #d1fae5; padding: 10px; border-radius: 10px; border: 1px solid #34d399; color: #065f46; margin-bottom: 20px;">
            <strong>✅ SYSTEM ACTIVE</strong><br>
            Monitoring Microphone & Messages in Real-time...
        </div>
    """, unsafe_allow_html=True)

    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simulation Hub", "Live Mic Test", "Manual Scan", "Live Logs", "Caregiver"])

    with tab1:
        st.header("⚡ Trigger Event")
        st.write("Simulate an external threat to see SafeEcho react automatically.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📞 Fake Call", use_container_width=True):
                simulate_call_interception()
        
        with col2:
            if st.button("📩 Fake SMS", use_container_width=True):
                simulate_message_interception()

    with tab2:
        st.header("🎤 Real-Time Audio Guardian")
        st.write("SafeEcho will listen continuously and flag scams as they happen.")
        
        # Language Selector
        lang = st.selectbox("Select Language", ["English", "Hindi", "Marathi"])
        
        # Session state for listening
        if 'listening' not in st.session_state:
            st.session_state.listening = False
            
        col1, col2 = st.columns(2)
        with col1:
            start_btn = st.button("▶️ Start Listening", type="primary", use_container_width=True)
        with col2:
            stop_btn = st.button("⏹️ Stop", type="secondary", use_container_width=True)
            
        if start_btn:
            st.session_state.listening = True
        if stop_btn:
            st.session_state.listening = False
            st.rerun()
            
        # Real-time Loop
        if st.session_state.listening:
            import speech_recognition as sr
            from deep_translator import GoogleTranslator
            
            st.success("👂 Listening... (Speak now)")
            status_container = st.empty()
            transcript_container = st.container()
            
            r = sr.Recognizer()
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.5 # Short pause to process chunks faster
            
            # Use the default microphone
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Continuous loop
                    while st.session_state.listening:
                        try:
                            status_container.info("Listening for phrase...")
                            # Listen for a short phrase (up to 5 seconds)
                            audio_data = r.listen(source, timeout=1, phrase_time_limit=5)
                            
                            status_container.warning("Processing...")
                            
                            # 1. Transcribe
                            lang_map = {"English": "en-US", "Hindi": "hi-IN", "Marathi": "mr-IN"}
                            api_lang = lang_map.get(lang, "en-US")
                            
                            text = r.recognize_google(audio_data, language=api_lang)
                            
                            # 2. Translate if needed
                            english_text = text
                            if lang != "English":
                                english_text = GoogleTranslator(source='auto', target='en').translate(text)
                            
                            # 3. Analyze
                            result = guardian.analyze_text(english_text)
                            
                            # 4. Display Result
                            with transcript_container:
                                with st.chat_message("user"):
                                    st.write(f"**You ({lang}):** {text}")
                                    if lang != "English":
                                        st.caption(f"Translated: {english_text}")
                                
                                if result["is_scam"]:
                                    with st.chat_message("assistant", avatar="🚨"):
                                        st.error(f"**SCAM DETECTED!** ({result['confidence']}%)")
                                        st.write(f"Reason: {result['reason']}")
                                        # Play alert sound (optional/simulated)
                                        # st.audio("alert.mp3", autoplay=True)
                                else:
                                    with st.chat_message("assistant", avatar="✅"):
                                        st.success("Safe.")
                                        
                        except sr.WaitTimeoutError:
                            continue # No speech detected, keep listening
                        except sr.UnknownValueError:
                            continue # Speech unintelligible
                        except Exception as e:
                            st.error(f"Error: {e}")
                            break
                            
            except Exception as e:
                st.error(f"Microphone Error: {e}. Make sure a microphone is connected.")
                st.session_state.listening = False

    with tab3:
        st.header("🔍 Manual Message Analysis")
        st.write("Paste any text or message below to check for scams.")
        
        user_text = st.text_area("Message Content", height=150, placeholder="e.g., 'Mom, I lost my phone, send money to this account...'")
        
        if st.button("Analyze Text"):
            if user_text:
                with st.spinner("Analyzing patterns..."):
                    import time
                    time.sleep(1)
                    result = guardian.analyze_text(user_text)
                
                if result["is_scam"]:
                    st.error(f"⚠️ **Potential Scam Detected** ({result['confidence']}%)")
                    st.write(f"**Reason:** {result['reason']}")
                else:
                    st.success(f"✅ **Safe Message** ({result['confidence']}% confidence)")
                    st.write(f"**Reason:** {result['reason']}")
            else:
                st.warning("Please enter some text first.")

    with tab4:
        st.header("🧠 Agent Logic")
        st.info("Waiting for events...")

    with tab5:
        st.header("Caregiver Dashboard")
        st.markdown("### 👵 Protected User: **Grandma Alice**")
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Threats Blocked", "12", "+2 today")
        m2.metric("Scam Calls", "5", "Last: 2h ago")
        m3.metric("System Status", "Active", "Online")
        
        st.divider()
        
        st.subheader("🚨 Recent Alert Log")
        
        # Fetch Real Data from DB
        real_data = db.get_alerts()
        
        if real_data:
            st.table(real_data)
        else:
            st.info("No alerts recorded yet. System is monitoring...")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.caption("Connected to SafeEcho Cloud (Simulated)")

def simulate_call_interception():
    """Simulates the autonomous loop for a call."""
    st.divider()
    
    # Step 1: Event Detection
    st.warning("📞 Incoming Call: Unknown Number (+1 555-0199)")
    st.toast("SafeEcho is listening...", icon="👂")
    
    # Step 2: Autonomous Analysis (Progress Bar)
    with st.spinner("🤖 SafeEcho is analyzing audio patterns..."):
        import time
        time.sleep(2) # Simulate processing time
        
        # Call the guardian brain
        result = guardian.analyze_audio("mock_audio_stream")
    
    # Step 3: Instant Verdict
    if result["is_scam"]:
        st.error(f"🚨 **SCAM BLOCKED!**")
        st.markdown(f"**Reason:** {result['reason']}")
        st.markdown(f"**Confidence:** {result['confidence']}%")
        st.caption("Caregiver has been notified.")
    else:
        st.success("✅ Call is Safe")

def simulate_message_interception():
    """Simulates the autonomous loop for a message."""
    st.divider()
    
    # Mock Message
    mock_msg = "URGENT: Your bank account is compromised. Click here to verify: http://bit.ly/scam"
    st.info(f"📩 New Message: '{mock_msg}'")
    
    # Step 2: Auto-Scan
    with st.spinner("🔍 Scanning text links and patterns..."):
        import time
        time.sleep(1.5)
        result = guardian.analyze_text(mock_msg)
    
    # Step 3: Verdict
    if result["is_scam"]:
        st.error(f"🚫 **MALICIOUS LINK DETECTED**")
        st.markdown(f"**Reason:** {result['reason']}")
        st.caption("Message quarantined.")
    else:
        st.success("✅ Message Safe")

if __name__ == "__main__":
    main()
