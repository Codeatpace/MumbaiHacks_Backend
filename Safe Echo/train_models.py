import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def load_dataset(filepath):
    """Loads the dataset from a file."""
    try:
        # Attempt to read as tab-separated, falling back if needed
        df = pd.read_csv(filepath, sep='\t', header=None, names=['label', 'text'], on_bad_lines='skip')
        
        # Check if it looks right (2 columns)
        if df.shape[1] != 2:
             # Try reading with a different separator or engine if needed, but for now assume tab based on preview
             print("Warning: Dataset might not be parsed correctly. Checking head:")
             print(df.head())

        # Map labels to 'scam' and 'safe'
        # File has 'fraud' and 'normal'
        label_map = {
            'fraud': 'scam',
            'normal': 'safe'
        }
        df['label'] = df['label'].map(label_map)
        
        # Drop rows with unmapped labels (if any)
        df = df.dropna(subset=['label'])
        
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def train_text_model():
    print("🧠 Training Text Scam Detector (SVM + Context)...")
    
    data_file = "fraud_call.file"
    if not os.path.exists(data_file):
        print(f"❌ Error: Dataset file '{data_file}' not found.")
        return

    df = load_dataset(data_file)
    if df is None or df.empty:
        print("❌ Error: Dataset is empty or could not be loaded.")
        return

    print(f"Loaded {len(df)} samples from main dataset.")

    # Load new scams
    new_scams_file = "new_scams.csv"
    if os.path.exists(new_scams_file):
        df_new = load_dataset(new_scams_file) # Re-using load_dataset might fail if format differs slightly, but let's check. 
        # Actually new_scams.csv is comma separated, fraud_call.file was tab separated but load_dataset handles csv with tab fallback?
        # Let's look at load_dataset again. It uses pd.read_csv with sep='\t'.
        # We should probably just read it directly since we know the format of new_scams.csv
        try:
            df_new = pd.read_csv(new_scams_file, header=None, names=['label', 'text'])
            # Ensure labels are mapped if needed, but they are already 'fraud'
            df_new['label'] = df_new['label'].map({'fraud': 'scam', 'normal': 'safe'})
            df_new = df_new.dropna(subset=['label'])
            print(f"Loaded {len(df_new)} samples from new scams.")
            df = pd.concat([df, df_new], ignore_index=True)
        except Exception as e:
            print(f"Error loading new scams: {e}")

    print(f"Total samples: {len(df)}")
    print(df['label'].value_counts())

    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

    # UPGRADE: Use TF-IDF with N-grams (1, 2) + Linear SVM (Logistic Regression mode)
    # Using 'log_loss' enables predict_proba() for confidence scores
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2)), 
        SGDClassifier(loss='log_loss', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None, class_weight='balanced')
    )
    
    # Train
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    print("Evaluating model...")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    # Retrain on full data for final model
    print("Retraining on full dataset...")
    model.fit(df['text'], df['label'])
    
    # Save
    joblib.dump(model, "text_model.pkl")
    print("✅ Model saved to 'text_model.pkl'")
    
    # Test
    test_msgs = [
        "Urgent update for your account",
        "Hey, are we still on for dinner?",
        "You have won a lottery! Claim now.",
        "Please send the report by EOD."
    ]
    
    print("\nTest Predictions:")
    for msg in test_msgs:
        # Get probability of 'scam' (assuming 'scam' is the second class, but we should check classes_)
        # SGDClassifier with log_loss gives probability
        prob = model.predict_proba([msg])[0]
        # Find index of 'scam' class
        scam_idx = list(model.classes_).index('scam')
        scam_prob = prob[scam_idx]
        
        print(f"'{msg}': {scam_prob:.4f} (Scam Probability)")

if __name__ == "__main__":
    train_text_model()
