const socket = new WebSocket(
  `ws://${window.location.host}/ws/interview/${window.SESSION_ID}/`
);

let recorder;
let audioChunks = [];

async function startStreamingVoice() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);

    recorder.ondataavailable = e => {
        if (e.data.size > 0 && socket.readyState === 1) {
            socket.send(e.data);
        }
    };

    recorder.start(300); // send chunk every 300ms
}

socket.onmessage = (event) => {
    if (typeof event.data === "string") {
        const msg = JSON.parse(event.data);
        if (msg.type === "text") {
            appendAIText(msg.delta);
        }
    } else {
        playAudioChunk(event.data);
    }
};

function playAudioChunk(blob) {
    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();
}
