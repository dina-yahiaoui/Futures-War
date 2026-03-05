// ============================================
// FUTURES WAR - SCRIPT PRINCIPAL
// ============================================

// Configuration
const API_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://btpia2026g1-futureswar.dokploy.atelier.ovh";
const API_TOKEN = "futures-war-secret-token-2026";

// État de l'application
let mediaRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let recordingSeconds = 0;

// Éléments DOM
const recordBtn = document.getElementById('recordBtn');
const recordingIndicator = document.getElementById('recordingIndicator');
const timerDisplay = document.getElementById('timer');
const transcriptionSection = document.getElementById('transcriptionSection');
const loadingTranscription = document.getElementById('loadingTranscription');
const transcriptionResult = document.getElementById('transcriptionResult');
const transcriptionText = document.getElementById('transcriptionText');
const generateBtn = document.getElementById('generateBtn');
const imageSection = document.getElementById('imageSection');
const loadingImage = document.getElementById('loadingImage');
const imageResult = document.getElementById('imageResult');
const generatedImage = document.getElementById('generatedImage');
const newImageBtn = document.getElementById('newImageBtn');
const errorMessage = document.getElementById('errorMessage');

// ============================================
// ENREGISTREMENT AUDIO
// ============================================

recordBtn.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        // Arrêter l'enregistrement
        stopRecording();
    } else {
        // Démarrer l'enregistrement
        startRecording();
    }
});

async function startRecording() {
    try {
        // Demander l'accès au micro
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        recordingSeconds = 0;

        // Collecter les données audio
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });

        // Traiter l'audio quand l'enregistrement s'arrête
        mediaRecorder.addEventListener('stop', () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioToAPI(audioBlob);
            
            // Arrêter le micro
            stream.getTracks().forEach(track => track.stop());
        });

        // Démarrer l'enregistrement
        mediaRecorder.start();

        // Mettre à jour l'UI
        recordBtn.classList.add('recording');
        recordBtn.querySelector('.text').textContent = 'Arrêter l\'enregistrement';
        recordingIndicator.classList.remove('hidden');

        // Démarrer le timer
        recordingTimer = setInterval(() => {
            recordingSeconds++;
            const minutes = Math.floor(recordingSeconds / 60);
            const seconds = recordingSeconds % 60;
            timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);

    } catch (error) {
        console.error('Erreur microphone:', error);
        showError('Impossible d\'accéder au microphone. Vérifiez les permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        
        // Réinitialiser l'UI
        recordBtn.classList.remove('recording');
        recordBtn.querySelector('.text').textContent = 'Appuyer pour parler';
        recordingIndicator.classList.add('hidden');
        
        // Arrêter le timer
        clearInterval(recordingTimer);
    }
}

// ============================================
// APPEL API - SPEECH TO TEXT
// ============================================

async function sendAudioToAPI(audioBlob) {
    try {
        // Afficher le loading
        loadingTranscription.classList.remove('hidden');
        transcriptionResult.classList.add('hidden');

        // Préparer les données
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.webm');

        // Appel API
        const response = await fetch(`${API_URL}/api/speech-to-text`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Afficher le résultat
        transcriptionText.textContent = data.text;
        loadingTranscription.classList.add('hidden');
        transcriptionResult.classList.remove('hidden');

    } catch (error) {
        console.error('Erreur transcription:', error);
        loadingTranscription.classList.add('hidden');
        showError('Erreur lors de la transcription. Vérifiez que l\'API est démarrée.');
    }
}

// ============================================
// APPEL API - PROMPT TO IMAGE
// ============================================

generateBtn.addEventListener('click', async () => {
    const prompt = transcriptionText.textContent;
    
    try {
        // Afficher le loading
        loadingImage.classList.remove('hidden');
        imageResult.classList.add('hidden');

        // Appel API
        const response = await fetch(`${API_URL}/api/prompt-to-image`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                width: 512,
                height: 512,
                steps: 9,
                guidance_scale: 0.0
            })
        });

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Afficher l'image
        generatedImage.src = `data:image/png;base64,${data.images[0]}`;
        loadingImage.classList.add('hidden');
        imageResult.classList.remove('hidden');

        // Scroll vers l'image
        imageSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Erreur génération:', error);
        loadingImage.classList.add('hidden');
        showError('Erreur lors de la génération. Le serveur GPU est-il accessible ?');
    }
});

// ============================================
// NOUVELLE IMAGE
// ============================================

newImageBtn.addEventListener('click', () => {
    // Réinitialiser tout
    transcriptionResult.classList.add('hidden');
    imageResult.classList.add('hidden');
    recordBtn.scrollIntoView({ behavior: 'smooth' });
});

// ============================================
// GESTION DES ERREURS
// ============================================

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');

    // Masquer après 5 secondes
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

// ============================================
// INITIALISATION
// ============================================

console.log('🚀 Futures War initialisé');
console.log(`📡 API: ${API_URL}`);