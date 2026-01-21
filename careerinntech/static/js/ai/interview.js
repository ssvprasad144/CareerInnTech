document.addEventListener("DOMContentLoaded", async function () {

    const chatBox = document.getElementById("chatBox");

    let currentAIAudio = null;
    let mediaRecorder;
    let audioChunks = [];
    let recording = false;

    // ==========================
    // CSRF
    // ==========================
    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    // ==========================
    // AI SPEAK
    // ==========================
    function playAudio(url) {
        if (!url) return;

        if (currentAIAudio) {
            currentAIAudio.pause();
            currentAIAudio = null;
        }

        currentAIAudio = new Audio(url);

        currentAIAudio.onended = () => {
            startVoiceInput(); // 🎙 auto listen after AI speaks
        };

        currentAIAudio.play().catch(() => {});
    }

    // ==========================
    // SEND MESSAGE (TEXT ONLY TO BACKEND)
    // ==========================
    async function sendMessage(text) {
        if (!text) return;

        chatBox.insertAdjacentHTML(
            "beforeend",
            `<div class="message user">${text}</div>`
        );
        chatBox.scrollTop = chatBox.scrollHeight;

        const res = await fetch("/ai/chat/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                session_id: window.SESSION_ID,
                message: text
            })
        });

        const data = await res.json();

        if (data.reply) {
            chatBox.insertAdjacentHTML(
                "beforeend",
                `<div class="message ai">${data.reply}</div>`
            );
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        if (data.audio_url) {
            playAudio(data.audio_url);
        }
    }

    // ==========================
    // 🎙 VOICE INPUT (AUTO)
    // ==========================
    async function startVoiceInput() {
        if (recording) return;

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        const audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 512;
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        recording = true;

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
            recording = false;
            audioContext.close();
            stream.getTracks().forEach(t => t.stop());

            const blob = new Blob(audioChunks, { type: "audio/webm" });
            const text = await sendAudioToBackend(blob);

            if (text) sendMessage(text);
        };

        mediaRecorder.start();

        let silenceStart = null;
        const SILENCE_THRESHOLD = 6;
        const SILENCE_DURATION = 1000;

        function detectSilence() {
            if (!recording) return;

            analyser.getByteFrequencyData(dataArray);
            const volume =
                dataArray.reduce((a, b) => a + b, 0) / dataArray.length;

            if (volume < SILENCE_THRESHOLD) {
                if (!silenceStart) silenceStart = Date.now();
                if (Date.now() - silenceStart > SILENCE_DURATION) {
                    mediaRecorder.stop();
                    return;
                }
            } else {
                silenceStart = null;
            }

            requestAnimationFrame(detectSilence);
        }

        detectSilence();
    }

    // ==========================
    // STT
    // ==========================
    async function sendAudioToBackend(blob) {
        const formData = new FormData();
        formData.append("audio", blob);
        formData.append("session_id", window.SESSION_ID);

        const res = await fetch("/ai/stt/", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        return data.text || "";
    }

    // ==========================
    // START INTERVIEW (AI FIRST)
    // ==========================
    await sendMessage("__START__");

});
