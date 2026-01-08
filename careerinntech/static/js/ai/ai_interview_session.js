let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startRecord");
const stopBtn = document.getElementById("stopRecord");
const statusText = document.getElementById("recordStatus");

startBtn.addEventListener("click", async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        audioChunks = [];
        mediaRecorder.start();

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusText.textContent = "🎙 Recording... Speak clearly.";

    } catch (err) {
        alert("Microphone access denied. Please allow mic permission.");
    }
});

stopBtn.addEventListener("click", () => {
    mediaRecorder.stop();

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        console.log("Recorded audio:", audioBlob);

        statusText.textContent = "✅ Answer recorded. Processing will happen next.";
    };

    startBtn.disabled = false;
    stopBtn.disabled = true;
});
