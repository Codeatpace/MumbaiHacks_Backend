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
        st.header("🎤 Live Conversation Monitor")
        st.write("Real-time analysis of ongoing conversation.")
        
        # Language Selector
        lang = st.selectbox("Select Language", ["English", "Hindi", "Marathi"])
        
        mode = st.radio("Mode", ["Single Record (File)", "Continuous Live Monitor (Local Mic)"])
        
        if mode == "Single Record (File)":
            # Audio Input
            audio_value = st.audio_input("Record Voice")
            
            if audio_value:
                st.audio(audio_value)
                
                with st.spinner(f"Listening & Translating ({lang})..."):
                    result = guardian.analyze_audio(audio_value, language=lang)
                
                # Display Results
                if "content_analysis" in result:
                    ca = result["content_analysis"]
                    
                    st.markdown("### 📝 Transcript")
                    st.info(f"**Original:** {ca.get('transcript', '...')}")
                    if lang != "English":
                        st.info(f"**Translated:** {ca.get('translation', '...')}")
                    
                    st.markdown("### 🛡️ Analysis")
                    if result["is_scam"]:
                        st.error(f"🚨 **SCAM DETECTED** ({result['confidence']}%)")
                        st.write(f"**Reason:** {result['reason']}")
                    else:
                        st.success("✅ **Audio seems Safe**")
                        st.write(f"**Reason:** {result['reason']}")

        else:
            # Continuous Mode
            st.info("🔴 **Live Monitoring Active**: Speak into your microphone. The system will analyze chunks of speech in real-time.")
            
            if st.button("Start Monitoring"):
                import speech_recognition as sr
                r = sr.Recognizer()
                r.energy_threshold = 300
                r.dynamic_energy_threshold = True
                
                status_placeholder = st.empty()
                transcript_placeholder = st.empty()
                alert_placeholder = st.empty()
                
                full_transcript = []
                
                with sr.Microphone() as source:
                    status_placeholder.warning("Adjusting for ambient noise... Please wait.")
                    r.adjust_for_ambient_noise(source, duration=1)
                    status_placeholder.success("Listening... (Refresh page to stop)")
                    
                    while True:
                        try:
                            # Listen for a phrase
                            audio_chunk = r.listen(source, phrase_time_limit=5)
                            
                            # Analyze
                            result = guardian.analyze_audio(audio_chunk, language=lang)
                            
                            if "content_analysis" in result:
                                ca = result["content_analysis"]
                                text = ca.get('transcript', '')
                                if text:
                                    full_transcript.append(f"You: {text}")
                                    transcript_placeholder.markdown("\n\n".join(full_transcript))
                                    
                                    if result["is_scam"]:
                                        alert_placeholder.error(f"🚨 SCAM DETECTED: {result['reason']}")
                                    else:
                                        alert_placeholder.success(f"✅ Safe: {result['reason']}")
                                        
                        except Exception as e:
                            status_placeholder.error(f"Error: {e}")
                            break

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
