# SafeEcho Backend (MumbaiHacks)

This repository contains the backend logic and the Streamlit prototype for SafeEcho, an AI-powered guardian against deepfakes and digital scams.

## Project Structure

- **Safe Echo/**: Contains the main Streamlit application and core logic.
  - `app.py`: The entry point for the Streamlit app.
  - `guardian.py`: Core logic for audio/text analysis and scam detection.
  - `db.py`: Simple JSON-based database for storing alerts.
  - `requirements.txt`: Python dependencies.

## Setup

### Prerequisites
- Python 3.9+
- `pip`
- `brew` (for macOS users, to install `flac`)

### Installation

1.  **Install System Dependencies (macOS)**:
    The audio processing library requires `flac`.
    ```bash
    brew install flac
    ```

2.  **Install Python Dependencies**:
    Navigate to the `Safe Echo` directory:
    ```bash
    cd "Safe Echo"
    pip install -r requirements.txt
    ```

3.  **Fix for Apple Silicon (M1/M2/M3)**:
    If you encounter "Bad CPU type" errors with `speech_recognition`, you may need to patch the library to use the system `flac` instead of the bundled one.
    ```bash
    # Example patch (adjust path to your python site-packages)
    mv ".../site-packages/speech_recognition/flac-mac" ".../site-packages/speech_recognition/flac-mac.bak"
    ```

## Usage

### Running the Streamlit App
This launches the mobile prototype simulation.

```bash
cd "Safe Echo"
python -m streamlit run app.py
```

Access the app at `http://localhost:8501`.

## Features
- **Simulation Hub**: Trigger fake calls and SMS to test the system.
- **Live Audio Analysis**: Real-time transcription and scam detection.
- **Caregiver Dashboard**: View alerts and blocked threats.

## Troubleshooting
- **Audio Transcription Errors**: Ensure `flac` is installed and the `speech_recognition` library is correctly configured (see Setup step 3).
- **Port Conflicts**: If port 8501 is busy, Streamlit will automatically try the next available port (8502, etc.).
