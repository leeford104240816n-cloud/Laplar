import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shazamio import Shazam
import speech_recognition as sr
from pydub import AudioSegment
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

shazam = Shazam()
recognizer = sr.Recognizer()

@app.get("/")
async def root():
    return {"message": "Music Detection API is running"}

async def transcribe_audio(file_path: str):
    """Transcribe audio to text using Google Web Speech API."""
    try:
        # Convert audio to wav if it's not already
        audio = AudioSegment.from_file(file_path)
        wav_path = f"{file_path}_{uuid.uuid4()}.wav"
        audio.export(wav_path, format="wav")

        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

@app.post("/detect")
async def detect_music(file: UploadFile = File(...)):
    # Use unique filename to avoid collisions
    unique_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    with open(unique_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Try recognition via fingerprinting (standard Shazam)
        try:
            out = await shazam.recognize(unique_filename)
            if out and 'track' in out:
                track = out['track']
                return {
                    "match": True,
                    "title": track.get('title'),
                    "subtitle": track.get('subtitle'),
                    "images": track.get('images'),
                    "method": "fingerprint"
                }
        except Exception as e:
            print(f"Fingerprinting error: {e}")

        # 2. If fingerprinting fails, try transcribing "singing" or lyrics
        lyrics = await transcribe_audio(unique_filename)
        if lyrics:
            # Search for track by lyrics/text
            try:
                search_results = await shazam.search_track(query=lyrics, limit=1)
                if search_results and 'tracks' in search_results and 'hits' in search_results['tracks']:
                    hits = search_results['tracks']['hits']
                    if hits:
                        track = hits[0]['track']
                        return {
                            "match": True,
                            "title": track.get('title'),
                            "subtitle": track.get('subtitle'),
                            "images": track.get('images'),
                            "method": "lyrics",
                            "transcribed_lyrics": lyrics
                        }
            except Exception as e:
                print(f"Lyrics search error: {e}")
                # Fallback to just returning transcribed lyrics if search fails
                return {"match": False, "message": "Heard lyrics but search failed", "transcribed_lyrics": lyrics}

        return {"match": False, "message": "No match found via fingerprinting or lyrics", "transcribed_lyrics": lyrics}

    except Exception as e:
        return {"match": False, "error": str(e)}
    finally:
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
