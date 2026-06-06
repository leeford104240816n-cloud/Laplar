# Laplar - Music Detection App

Laplar is a music detection application similar to Shazam, but with the added ability to identify songs by singing lyrics.

## Features
- **Audio Fingerprinting**: Uses Shazam's core technology to identify original tracks.
- **Singing Support**: Transcribes your singing into text and searches for the song based on the lyrics.
- **Simple Web Interface**: Easy-to-use "Start Identification" button.

## Prerequisites

- **Python 3.10+**
- **FFmpeg**: Required for audio processing.
  - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - On macOS: `brew install ffmpeg`
  - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

1. Clone the repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

### 1. Start the Backend
Navigate to the root directory and run:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend
Since the frontend is a static site, you can simply open `frontend/index.html` in your web browser.

Alternatively, you can serve it using Python:
```bash
python3 -m http.server 3000 --directory frontend
```
Then navigate to `http://localhost:3000`.

## How to Test

1. Ensure the backend is running.
2. Open the frontend in a browser (Chrome or Edge recommended for best microphone support).
3. Click **"Start Identification"**.
4. Play a song or sing some lyrics into your microphone.
5. Click **"Stop Recording"**.
6. Wait for the app to analyze the audio and display the result.

## Project Structure
- `backend/main.py`: FastAPI server handling audio fingerprinting and transcription.
- `frontend/`: HTML and JavaScript for the web interface.
- `requirements.txt`: Python dependencies.
