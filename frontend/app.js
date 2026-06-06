const recordBtn = document.getElementById('recordBtn');
const statusDiv = document.getElementById('status');
const resultDiv = document.getElementById('result');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudioToBackend(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        recordBtn.innerText = 'Stop Recording (listening...)';
        recordBtn.classList.add('recording');
        statusDiv.innerText = 'Listening for music/singing...';
    } catch (err) {
        console.error('Error accessing microphone:', err);
        statusDiv.innerText = 'Error: Microphone access denied';
    }
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    recordBtn.innerText = 'Start Identification';
    recordBtn.classList.remove('recording');
    statusDiv.innerText = 'Processing audio...';
    resultDiv.innerHTML = '<p class="loading">Analyzing your audio, please wait...</p>';
}

async function sendAudioToBackend(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');

    try {
        const response = await fetch('http://localhost:8000/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        displayResult(data);
    } catch (err) {
        console.error('Error sending audio to backend:', err);
        statusDiv.innerText = 'Error connecting to server';
        resultDiv.innerHTML = '<p>Could not reach the backend server.</p>';
    }
}

function displayResult(data) {
    if (data.match) {
        statusDiv.innerText = 'Match Found!';
        let html = `
            <div class="track-info">
                ${data.images && data.images.coverart ? `<img src="${data.images.coverart}" alt="Cover Art">` : ''}
                <div class="track-title">${data.title}</div>
                <div class="track-artist">${data.subtitle}</div>
                <div class="method-tag">Detected via ${data.method}</div>
                ${data.transcribed_lyrics ? `<p style="font-size: 0.8rem; color: #666; margin-top: 10px;">Lyrics heard: "${data.transcribed_lyrics}"</p>` : ''}
            </div>
        `;
        resultDiv.innerHTML = html;
    } else {
        statusDiv.innerText = 'No match found';
        resultDiv.innerHTML = `<p>${data.message || 'Sorry, we couldn\'t identify that song.'}</p>
        ${data.transcribed_lyrics ? `<p style="font-size: 0.8rem; color: #666;">We heard: "${data.transcribed_lyrics}" but no song matched.</p>` : ''}`;
    }
}
