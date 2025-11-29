import guardian
import joblib

def verify_detection():
    print("🔍 Verifying Detection Logic...")

    # Load model to ensure it's the latest
    try:
        guardian.model = joblib.load("text_model.pkl")
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    test_cases = [
        {
            "text": "Your Netflix account will be suspended today unless you update payment info here: [link]",
            "context": {"is_saved_contact": False},
            "expected_scam": True,
            "desc": "Known Scam (Unknown Number)"
        },
        {
            "text": "Hey, are we still on for dinner tonight?",
            "context": {"is_saved_contact": True},
            "expected_scam": False,
            "desc": "Safe Message (Saved Contact)"
        },
        {
            "text": "Please verify your account immediately.",
            "context": {"is_saved_contact": True},
            "expected_scam": False, # Should be safe because it's a saved contact, even with "verify"
            "desc": "Suspicious Keyword (Saved Contact) -> Should be Safe due to high threshold"
        },
        {
            "text": "Please verify your account immediately.",
            "context": {"is_saved_contact": False},
            "expected_scam": True, # Should be scam or flagged due to keyword/model
            "desc": "Suspicious Keyword (Unknown Number) -> Should be Scam"
        },
        {
             "text": "Urgent: Your Wells Fargo card starting ****1234 was used at Target $412. Confirm or decline?",
             "context": {"is_saved_contact": False},
             "expected_scam": True,
             "desc": "New Scam from List (Unknown Number)"
        },
        {
             "text": "mom I  need 50,000, pls transfer that money in Uncles UPI",
             "context": {"is_saved_contact": False},
             "expected_scam": True,
             "desc": "User Reported Family Emergency Scam (Unknown Number)"
        }
    ]

    with open("verification_output.txt", "w", encoding="utf-8") as f:
        for case in test_cases:
            f.write(f"\nTesting: {case['desc']}\n")
            f.write(f"Text: {case['text']}\n")
            f.write(f"Context: {case['context']}\n")
            
            result = guardian.analyze_text(case['text'], context=case['context'])
            f.write(f"Result: {result}\n")
            
            if result['is_scam'] == case['expected_scam']:
                f.write("✅ PASS\n")
            else:
                f.write(f"❌ FAIL (Expected is_scam={case['expected_scam']}, got {result['is_scam']})\n")

if __name__ == "__main__":
    verify_detection()
