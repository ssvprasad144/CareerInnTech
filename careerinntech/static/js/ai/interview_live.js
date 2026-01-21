document.addEventListener("DOMContentLoaded", () => {

    /* ================= CORE STATE ================= */
    const SESSION_ID = window.SESSION_ID;
    const INTERVIEW_CONFIG = window.INTERVIEW_CONFIG || {};

    let stream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let recording = false;

    let interviewStarted = false;
    let introCompleted = false;

    let audioContext = null;
    let analyser = null;
    let dataArray = null;

    let currentAIAudio = null;
    let currentAIRequestController = null;
    let currentSttRequestController = null;
    let lastAudioUrl = null;
    let lastAIText = null;
    let pendingAutoFinish = false;
    let currentUtterance = null;
    let preferredVoice = null;
    const preferBrowserTts = true;
    // Browser STT (Web Speech API) — used as primary. Fallback to server `/ai/stt/` when needed.
    let browserRecognitionSupported = false;
    let browserRecognition = null;
    let browserSttTranscript = null;
    let browserSttConfidence = null;
    let browserSttActive = false;
    let suppressNextAnswer = false;
    let audioPaused = false;
    let extraAnswerTimeMs = 0;

    let questionIndex = 0;
    let totalQuestions = Number(INTERVIEW_CONFIG.questionCount || 10);

    let recordingStartAt = null;

    let micMeterContext = null;
    let micMeterAnalyser = null;
    let micMeterData = null;
    let micMeterActive = false;

    const speechMetrics = {
        totalAnswers: 0,
        totalWords: 0,
        totalSeconds: 0,
        fillerCount: 0,
        clarityScore: 0,
        avgWpm: 0,
        paceLabel: "--"
    };

    const faceMetrics = {
        totalSamples: 0,
        detectedSamples: 0,
        awayCount: 0,
        faceAreaSum: 0,
        maxFaces: 0,
        presencePct: 0,
        avgFaceSizePct: 0,
        expressionLabel: "--"
    };

    let faceDetector = null;
    let faceSampleTimer = null;

    const transcriptsCache = [];

    try {
        const cached = localStorage.getItem("aiInterviewTranscripts");
        if (cached) {
            const parsed = JSON.parse(cached);
            if (Array.isArray(parsed)) {
                transcriptsCache.push(...parsed);
            }
        }
    } catch (e) {}

    /* ================= CAMERA STATE ================= */
    let cameraStream = null;
    const videoEl = document.getElementById("userCamera");
    const cameraPlaceholder = document.getElementById("cameraPlaceholder");

    /* ================= EXIT STATE ================= */
    let interviewFinished = false;
    let finishingInProgress = false;

    /* ================= DOM ================= */
    const timerEl = document.getElementById("timer");
    const startPauseBtn = document.getElementById("startPauseBtn");
    const endBtn = document.getElementById("endInterview");
    const aiAvatar = document.getElementById("aiAvatar");
    const aiTextEl = document.getElementById("aiText");
    const feedbackLoading = document.getElementById("feedbackLoading");
    const audioToggleBtn = document.getElementById("audioToggleBtn");
    const textOnlyBtn = document.getElementById("textOnlyBtn");
    const hintBtn = document.getElementById("hintBtn");
    const skipBtn = document.getElementById("skipBtn");
    const notesBtn = document.getElementById("notesBtn");
    const codeBtn = document.getElementById("codeBtn");
    const submitCodeBtn = document.getElementById("submitCodeBtn");
    const codeDrawer = document.getElementById("codeDrawer");
    const codeClose = document.getElementById("codeClose");
    const codeInput = document.getElementById("codeInput");
    const sendCodeBtn = document.getElementById("sendCodeBtn");
    const extendBtn = document.getElementById("extendBtn");
    const textOnlyModal = document.getElementById("textOnlyModal");
    const textOnlyContent = document.getElementById("textOnlyContent");
    const textOnlyClose = document.getElementById("textOnlyClose");
    const notesDrawer = document.getElementById("notesDrawer");
    const notesClose = document.getElementById("notesClose");
    const notesInput = document.getElementById("notesInput");
    const actionToast = document.getElementById("actionToast");
    const latencyValue = document.getElementById("latencyValue");
    const liveTips = document.getElementById("liveTips");
    const micCheckBtn = document.getElementById("micCheckBtn");
    const micLevelEl = document.getElementById("micLevel");
    const networkStatus = document.getElementById("networkStatus");
    const questionProgress = document.getElementById("questionProgress");
    const rubricList = document.getElementById("rubricList");
    const faceStatus = document.getElementById("faceStatus");
    const fluencyLevel = document.getElementById("fluencyLevel");
    const clarityLevel = document.getElementById("clarityLevel");
    const expressionLevel = document.getElementById("expressionLevel");
    const fluencyLabel = document.getElementById("fluencyLabel");
    const clarityLabel = document.getElementById("clarityLabel");
    const expressionLabel = document.getElementById("expressionLabel");
    const gazeToast = document.getElementById("gazeToast");

    /* ================= AI AVATAR ================= */
    function setAIState(state) {
        if (!aiAvatar) return;
        aiAvatar.classList.remove("idle", "speaking", "listening");
        aiAvatar.classList.add(state);
    }
    setAIState("idle");

    /* ================= TIMER (COUNT UP) ================= */
    let seconds = 0;
    let timerInterval = null;

    function startTimer() {
        if (timerInterval) return;
        timerInterval = setInterval(() => {
            seconds++;
            const m = String(Math.floor(seconds / 60)).padStart(2, "0");
            const s = String(seconds % 60).padStart(2, "0");
            timerEl.textContent = `${m}:${s}`;
        }, 1000);
    }

    function pauseTimer() {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    /* ================= MIC ================= */
    async function requestMic() {
        if (stream) return;
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setupMicMeter();
    }

    function startBrowserRecognition() {
        browserSttTranscript = null;
        browserSttConfidence = null;
        if (browserSttActive) return;
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) return;
        try {
            browserRecognitionSupported = true;
            browserRecognition = new SpeechRec();
            browserRecognition.lang = 'en-US';
            browserRecognition.interimResults = true;
            browserRecognition.maxAlternatives = 1;
            browserSttActive = true;

            let interim = '';
            browserRecognition.onresult = (evt) => {
                interim = '';
                let finalText = '';
                for (let i = evt.resultIndex; i < evt.results.length; ++i) {
                    const res = evt.results[i];
                    if (res.isFinal) {
                        finalText += res[0].transcript + ' ';
                        // confidence may be available on some browsers
                        if (res[0] && typeof res[0].confidence === 'number') {
                            browserSttConfidence = res[0].confidence;
                        }
                    } else {
                        interim += res[0].transcript;
                    }
                }
                if (finalText && finalText.trim().length) {
                    browserSttTranscript = finalText.trim();
                }
            };

            browserRecognition.onerror = () => {
                browserSttActive = false;
            };

            browserRecognition.onend = () => {
                browserSttActive = false;
            };

            try { browserRecognition.start(); } catch (e) { browserSttActive = false; }
        } catch (e) {
            browserRecognitionSupported = false;
            browserSttActive = false;
        }
    }

    function stopBrowserRecognition() {
        try {
            if (browserRecognition && browserSttActive) {
                browserRecognition.onresult = null;
                browserRecognition.onend = null;
                browserRecognition.onerror = null;
                try { browserRecognition.stop(); } catch (e) {}
            }
        } finally {
            browserSttActive = false;
            browserRecognition = null;
        }
    }

    /* ================= CAMERA ================= */
    async function startCamera() {
        if (cameraStream) return;

        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user" },
            audio: false
        });

        videoEl.srcObject = cameraStream;
        videoEl.style.display = "block";
        cameraPlaceholder.style.display = "none";

        initFaceDetection();
    }

    function stopCamera() {
        if (!cameraStream) return;

        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;

        videoEl.srcObject = null;
        videoEl.style.display = "none";
        cameraPlaceholder.style.display = "flex";

        stopFaceDetection();
    }

    function updateNetworkStatus() {
        if (!networkStatus) return;
        if (navigator.onLine) {
            networkStatus.textContent = "Online";
            networkStatus.classList.remove("offline");
        } else {
            networkStatus.textContent = "Offline";
            networkStatus.classList.add("offline");
        }
    }

    function updateQuestionProgress() {
        if (!questionProgress) return;
        questionProgress.textContent = `Questions: ${questionIndex}/${totalQuestions}`;
    }

    function initFaceDetection() {
        if (!faceStatus) return;
        if (!window.FaceDetector) {
            faceStatus.textContent = "Not supported";
            faceStatus.classList.add("offline");
            return;
        }
        faceDetector = new FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
        faceStatus.textContent = "Detecting…";
        faceStatus.classList.remove("offline");
        if (faceSampleTimer) return;
        faceSampleTimer = setInterval(sampleFace, 1500);
    }

    function stopFaceDetection() {
        if (faceSampleTimer) {
            clearInterval(faceSampleTimer);
            faceSampleTimer = null;
        }
    }

    async function sampleFace() {
        if (!faceDetector || !videoEl || videoEl.readyState < 2) return;
        try {
            const faces = await faceDetector.detect(videoEl);
            faceMetrics.totalSamples += 1;

            if (faces.length > 0) {
                faceMetrics.detectedSamples += 1;
                faceMetrics.maxFaces = Math.max(faceMetrics.maxFaces, faces.length);
                const box = faces[0].boundingBox;
                const videoArea = (videoEl.videoWidth || 1) * (videoEl.videoHeight || 1);
                const faceArea = Math.max(1, box.width * box.height);
                const faceRatio = faceArea / videoArea;
                faceMetrics.faceAreaSum += faceRatio;

                const centerX = box.x + box.width / 2;
                const centerY = box.y + box.height / 2;
                const xOffset = Math.abs(centerX - (videoEl.videoWidth / 2)) / (videoEl.videoWidth / 2);
                const yOffset = Math.abs(centerY - (videoEl.videoHeight / 2)) / (videoEl.videoHeight / 2);
                const lookingAway = xOffset > 0.35 || yOffset > 0.35;
                showGazeWarning(lookingAway);

                faceStatus.textContent = "Detected";
                faceStatus.classList.remove("offline");
            } else {
                faceMetrics.awayCount += 1;
                faceStatus.textContent = "Not detected";
                faceStatus.classList.add("offline");
                showGazeWarning(true);
            }

            finalizeFaceMetrics();
            updateExpressionMeter();
        } catch (e) {
            faceStatus.textContent = "Unavailable";
            faceStatus.classList.add("offline");
            showGazeWarning(false);
        }
    }

    function finalizeFaceMetrics() {
        const total = Math.max(1, faceMetrics.totalSamples);
        faceMetrics.presencePct = Math.round((faceMetrics.detectedSamples / total) * 100);
        const avgFace = faceMetrics.faceAreaSum / Math.max(1, faceMetrics.detectedSamples);
        faceMetrics.avgFaceSizePct = Math.round(avgFace * 100);

        if (faceMetrics.presencePct >= 80 && faceMetrics.avgFaceSizePct >= 5) {
            faceMetrics.expressionLabel = "Engaged";
        } else if (faceMetrics.presencePct >= 60) {
            faceMetrics.expressionLabel = "Neutral";
        } else {
            faceMetrics.expressionLabel = "Low engagement";
        }
    }

    function setupMicMeter() {
        if (!stream || micMeterActive) return;
        micMeterContext = new AudioContext();
        const source = micMeterContext.createMediaStreamSource(stream);
        micMeterAnalyser = micMeterContext.createAnalyser();
        micMeterAnalyser.fftSize = 256;
        source.connect(micMeterAnalyser);
        micMeterData = new Uint8Array(micMeterAnalyser.frequencyBinCount);
        micMeterActive = true;
        updateMicMeter();
    }

    function stopMicMeter() {
        micMeterActive = false;
        if (micMeterContext) {
            micMeterContext.close().catch(() => {});
            micMeterContext = null;
        }
    }

    function updateMicMeter() {
        if (!micMeterActive || !micMeterAnalyser || !micMeterData) return;
        micMeterAnalyser.getByteFrequencyData(micMeterData);
        const volume = micMeterData.reduce((a, b) => a + b, 0) / micMeterData.length;
        const percent = Math.min(100, Math.max(0, Math.round((volume / 50) * 100)));
        if (micLevelEl) micLevelEl.style.width = `${percent}%`;
        requestAnimationFrame(updateMicMeter);
    }

    /* ================= AI AUDIO ================= */
    function playAIAudio(url, text, playbackRate = 1) {
        if (interviewFinished) return;

        if (currentAIAudio) currentAIAudio.pause();
        stopBrowserTts();
        audioPaused = false;
        updateAudioToggleLabel();
        audioPaused = false;
        updateAudioToggleLabel();

        if (text && aiTextEl) {
            aiTextEl.innerText = "";
            setTimeout(() => aiTextEl.innerText = text, 30);
        }

        setAIState("speaking");

        lastAIText = text || lastAIText;

        if (!url || preferBrowserTts) {
            speakWithBrowserTts(lastAIText, playbackRate);
            return;
        }

        currentAIAudio = new Audio(url);
        currentAIAudio.playbackRate = playbackRate;
        lastAudioUrl = url;
        if (audioToggleBtn) audioToggleBtn.disabled = false;
        if (textOnlyBtn) textOnlyBtn.disabled = false;
        if (hintBtn) hintBtn.disabled = false;
        if (skipBtn) skipBtn.disabled = false;
        currentAIAudio.onended = () => {
            if (!interviewStarted || interviewFinished) return;
            setAIState("listening");
            if (pendingAutoFinish) {
                finishInterview("auto_complete");
                return;
            }
            startRecording();
        };

        currentAIAudio.onerror = () => {
            speakWithBrowserTts(lastAIText, playbackRate);
        };

        currentAIAudio.play().catch(() => {
            speakWithBrowserTts(lastAIText, playbackRate);
        });
    }

    function speakWithBrowserTts(text, playbackRate = 1) {
        if (!text || !window.speechSynthesis) return;
        stopBrowserTts();
        audioPaused = false;
        updateAudioToggleLabel();

        const utterance = new SpeechSynthesisUtterance(text);
        if (preferredVoice) utterance.voice = preferredVoice;
        utterance.rate = playbackRate;
        currentUtterance = utterance;

        utterance.onend = () => {
            currentUtterance = null;
            if (!interviewStarted || interviewFinished) return;
            setAIState("listening");
            if (pendingAutoFinish) {
                finishInterview("auto_complete");
                return;
            }
            startRecording();
        };

        utterance.onerror = () => {
            currentUtterance = null;
            if (!interviewStarted || interviewFinished) return;
            setAIState("listening");
            startRecording();
        };

        if (audioToggleBtn) audioToggleBtn.disabled = false;
        if (textOnlyBtn) textOnlyBtn.disabled = false;
        if (hintBtn) hintBtn.disabled = false;
        if (skipBtn) skipBtn.disabled = false;

        window.speechSynthesis.speak(utterance);
    }

    function stopBrowserTts() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        currentUtterance = null;
        audioPaused = false;
        updateAudioToggleLabel();
    }

    function updateAudioToggleLabel() {
        if (!audioToggleBtn) return;
        audioToggleBtn.textContent = audioPaused ? "Resume Audio" : "Pause Audio";
    }

    function pauseAudio() {
        if (currentAIAudio && !currentAIAudio.paused) currentAIAudio.pause();
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.pause();
        }
        audioPaused = true;
        updateAudioToggleLabel();
    }

    function resumeAudio() {
        if (currentAIAudio && currentAIAudio.paused) {
            currentAIAudio.play().catch(() => {});
        }
        if (window.speechSynthesis && window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        }
        audioPaused = false;
        updateAudioToggleLabel();
    }

    /* ================= RECORD USER ================= */
    function startRecording() {
        if (!interviewStarted || interviewFinished || recording || !stream) return;
        // reset browser STT transcript for this answer
        browserSttTranscript = null;
        browserSttConfidence = null;

        audioChunks = [];
        recording = true;
        recordingStartAt = Date.now();

        audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 512;
        source.connect(analyser);
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
            recording = false;
            audioContext.close();
            setAIState("idle");

            if (!audioChunks.length || !interviewStarted) return;
            if (suppressNextAnswer) {
                suppressNextAnswer = false;
                return;
            }
            const durationMs = Date.now() - (recordingStartAt || Date.now());
            // stop browser recognition (we'll prefer its transcript if available)
            try { stopBrowserRecognition(); } catch (e) {}
            await processAnswer(durationMs);
        };

        mediaRecorder.start();
        // start browser-side speech recognition in parallel (preferred)
        startBrowserRecognition();
        detectSilence();
    }

    /* ================= SILENCE DETECTION ================= */
    function detectSilence() {
        let silenceStart = null;
        let hasSpoken = false;

        const SILENCE_THRESHOLD = 10;
        const MIN_SPEECH_TIME = 1500 + extraAnswerTimeMs;
        const SILENCE_DURATION = 1800 + extraAnswerTimeMs;
        const speechStartTime = Date.now();

        function loop() {
            if (!recording) return;

            analyser.getByteFrequencyData(dataArray);
            const volume =
                dataArray.reduce((a, b) => a + b, 0) / dataArray.length;

            if (volume > SILENCE_THRESHOLD) {
                hasSpoken = true;
                silenceStart = null;
            } else if (hasSpoken) {
                if (!silenceStart) silenceStart = Date.now();

                if (
                    Date.now() - silenceStart > SILENCE_DURATION &&
                    Date.now() - speechStartTime > MIN_SPEECH_TIME
                ) {
                    if (mediaRecorder?.state === "recording") {
                        mediaRecorder.stop();
                    }
                    extraAnswerTimeMs = 0;
                    return;
                }
            }
            requestAnimationFrame(loop);
        }
        loop();
    }

    /* ================= PROCESS ANSWER ================= */
    async function processAnswer(durationMs) {
        if (interviewFinished || !interviewStarted) return;
        // Prefer browser STT transcript if available and confident enough
        let transcript = null;
        if (browserSttTranscript && browserSttTranscript.trim().length >= 10) {
            // If confidence is reported use threshold, otherwise accept
            if (browserSttConfidence == null || browserSttConfidence >= 0.6) {
                transcript = browserSttTranscript.trim();
                if (latencyValue) latencyValue.textContent = `client STT`;
            }
        }

        let sttData = null;
        if (!transcript) {
            // fallback: upload audio to server `/ai/stt/`
            const blob = new Blob(audioChunks, { type: "audio/webm" });
            const form = new FormData();
            form.append("audio", blob);

            const sttStart = performance.now();
            if (currentSttRequestController) currentSttRequestController.abort();
            currentSttRequestController = new AbortController();

            try {
                const sttRes = await fetchWithTimeout("/ai/stt/", {
                    method: "POST",
                    body: form,
                    signal: currentSttRequestController.signal
                }, 12000);
                sttData = await sttRes.json();
            } catch (e) {
                try {
                    const retryRes = await fetchWithTimeout("/ai/stt/", {
                        method: "POST",
                        body: form,
                        signal: currentSttRequestController.signal
                    }, 12000);
                    sttData = await retryRes.json();
                } catch {
                    aiTextEl.textContent = "Network issue while transcribing. Please answer again.";
                    setAIState("listening");
                    startRecording();
                    return;
                }
            }

            const sttLatency = Math.round(performance.now() - sttStart);
            if (latencyValue) latencyValue.textContent = `${sttLatency} ms`;

            if (!sttData || !sttData.text || sttData.text.trim().length < 10) {
                setAIState("listening");
                startRecording();
                return;
            }

            transcript = sttData.text.trim();
        }
        // record STT source for telemetry: prefer browser when available
        const sttSource = (browserSttTranscript && browserSttTranscript.trim().length >= 10 && (browserSttConfidence == null || browserSttConfidence >= 0.6)) ? 'client' : 'server';
        transcriptsCache.push({ text: transcript, ts: Date.now(), stt_source: sttSource });
        localStorage.setItem("aiInterviewTranscripts", JSON.stringify(transcriptsCache));

        updateSpeechMetrics(transcript, durationMs || 1);

        const aiStart = performance.now();
        if (currentAIRequestController) currentAIRequestController.abort();
        currentAIRequestController = new AbortController();

        let aiData = null;
        try {
            const aiRes = await fetchWithTimeout("/ai/voice/next/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: SESSION_ID, text: transcript, stt_source: sttSource }),
                signal: currentAIRequestController.signal
            }, 15000);
            aiData = await aiRes.json();
        } catch (e) {
            try {
                const retryRes = await fetchWithTimeout("/ai/voice/next/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, text: transcript }),
                    signal: currentAIRequestController.signal
                }, 15000);
                aiData = await retryRes.json();
            } catch {
                aiTextEl.textContent = "Network issue while generating next question. Please try again.";
                setAIState("listening");
                startRecording();
                return;
            }
        }

        if (interviewFinished) return;
        const aiLatency = Math.round(performance.now() - aiStart);
        if (latencyValue) latencyValue.textContent = `${aiLatency} ms`;

        if (typeof aiData.question_index === "number") {
            questionIndex = aiData.question_index;
        }
        if (typeof aiData.total_questions === "number") {
            totalQuestions = aiData.total_questions;
        }
        updateQuestionProgress();

        if (aiData.phase === "complete") {
            // show feedback loading and auto-finish immediately
            pendingAutoFinish = true;
            if (feedbackLoading) {
                feedbackLoading.classList.add("active");
                feedbackLoading.setAttribute("aria-hidden", "false");
            }
            // call finish without waiting for audio end
            await finishInterview("auto_complete");
            return;
        }

        // If server requests code editor for this question, open drawer and show hint
        if (aiData.use_code_editor) {
            if (codeDrawer) {
                codeDrawer.setAttribute('aria-hidden', 'false');
                codeDrawer.style.display = 'block';
            }
            if (aiTextEl) {
                aiTextEl.innerText = (aiData.text || "") + "\n\n(Please use the code editor below for this question; press Send Code when ready.)";
            }
            // do not start recording; wait for user to send code
            return;
        }

        playAIAudio(aiData.audio_url, aiData.text);
    }

    function updateSpeechMetrics(transcript, durationMs) {
        const words = transcript.split(/\s+/).filter(Boolean);
        const wordCount = words.length;
        const seconds = Math.max(1, Math.round(durationMs / 1000));

        const fillerWords = ["um", "uh", "like", "you know", "actually", "basically", "so"];
        let fillerCount = 0;
        const lower = transcript.toLowerCase();
        fillerWords.forEach(fw => {
            const re = new RegExp(`\\b${fw}\\b`, "g");
            const matches = lower.match(re);
            if (matches) fillerCount += matches.length;
        });

        speechMetrics.totalAnswers += 1;
        speechMetrics.totalWords += wordCount;
        speechMetrics.totalSeconds += seconds;
        speechMetrics.fillerCount += fillerCount;

        const wpm = Math.round((speechMetrics.totalWords / Math.max(1, speechMetrics.totalSeconds)) * 60);
        speechMetrics.avgWpm = wpm;

        if (wpm < 90) speechMetrics.paceLabel = "Slow";
        else if (wpm > 150) speechMetrics.paceLabel = "Fast";
        else speechMetrics.paceLabel = "Good";

        const fillerPenalty = Math.min(40, Math.round((speechMetrics.fillerCount / Math.max(1, speechMetrics.totalWords)) * 100));
        const lengthPenalty = wordCount < 25 ? 15 : 0;
        speechMetrics.clarityScore = Math.max(0, 100 - fillerPenalty - lengthPenalty);

        updateLiveTips(wordCount, wpm, fillerCount);
        updateSpeechMeters();
    }

    function updateLiveTips(wordCount, wpm, fillerCount) {
        if (!liveTips) return;
        liveTips.innerHTML = "";
        const tips = [];

        if (wordCount < 25) tips.push("Answer was short. Add one more example or detail.");
        if (wpm > 150) tips.push("You spoke fast. Slow down slightly for clarity.");
        if (wpm < 90) tips.push("You spoke slowly. Aim for a steady pace.");
        if (fillerCount >= 3) tips.push("Try reducing filler words like 'um' and 'like'.");

        if (!tips.length) tips.push("Great pace and clarity. Keep it up!");

        tips.slice(0, 3).forEach(tip => {
            const li = document.createElement("li");
            li.textContent = tip;
            liveTips.appendChild(li);
        });
    }

    function updateSpeechMeters() {
        if (!fluencyLevel || !clarityLevel) return;
        const wpm = speechMetrics.avgWpm || 0;
        const fluencyPct = Math.max(0, Math.min(100, Math.round((Math.min(wpm, 170) / 170) * 100)));
        const clarityPct = Math.max(0, Math.min(100, speechMetrics.clarityScore || 0));

        fluencyLevel.style.width = `${fluencyPct}%`;
        clarityLevel.style.width = `${clarityPct}%`;

        setMeterTone(fluencyLevel, fluencyPct);
        setMeterTone(clarityLevel, clarityPct);

        if (fluencyLabel) fluencyLabel.textContent = wpm ? `${wpm} WPM` : "--";
        if (clarityLabel) clarityLabel.textContent = clarityPct ? `${clarityPct}%` : "--";
    }

    function updateExpressionMeter() {
        if (!expressionLevel) return;
        const engagement = Math.max(0, Math.min(100, faceMetrics.presencePct || 0));
        expressionLevel.style.width = `${engagement}%`;
        setMeterTone(expressionLevel, engagement);
        if (expressionLabel) expressionLabel.textContent = faceMetrics.expressionLabel || "--";
    }

    function setMeterTone(el, value) {
        if (!el) return;
        el.classList.remove("warning", "danger");
        if (value < 40) el.classList.add("danger");
        else if (value < 65) el.classList.add("warning");
    }

    function showGazeWarning(show) {
        if (!gazeToast) return;
        if (show) gazeToast.classList.add("show");
        else gazeToast.classList.remove("show");
    }

    function showActionToast(message) {
        if (!actionToast) return;
        actionToast.textContent = message;
        actionToast.classList.add("show");
        setTimeout(() => actionToast.classList.remove("show"), 1200);
    }

    function fetchWithTimeout(url, options, timeoutMs) {
        const controller = new AbortController();
        if (options?.signal) {
            if (options.signal.aborted) controller.abort();
            else options.signal.addEventListener("abort", () => controller.abort(), { once: true });
        }
        const timeout = setTimeout(() => controller.abort(), timeoutMs);
        const mergedOptions = { ...options, signal: controller.signal };
        return fetch(url, mergedOptions).finally(() => clearTimeout(timeout));
    }

    /* ================= FINISH INTERVIEW (CENTRAL) ================= */
    async function finishInterview(reason = "exit") {
        if (finishingInProgress || interviewFinished) return false;
        finishingInProgress = true;

        // Skip confirmation when auto-completing at natural end of interview
        const needsConfirmation = (reason !== 'auto_complete') && (interviewStarted || introCompleted || recording);
        if (needsConfirmation) {
            const confirmed = confirm(
                "⚠️ If you leave now, the interview will end and feedback will be generated.\n\nDo you want to continue?"
            );

            if (!confirmed) {
                finishingInProgress = false;
                return false;
            }
        }

        interviewStarted = false;
        interviewFinished = true;
        disableExitGuard();
        pauseTimer();
        if (endBtn) endBtn.disabled = true;
        if (feedbackLoading) {
            feedbackLoading.classList.add("active");
            feedbackLoading.setAttribute("aria-hidden", "false");
        }
        document.body.classList.add("feedback-loading-active");
        await new Promise(requestAnimationFrame);
        await new Promise(resolve => setTimeout(resolve, 1200));
        if (currentAIRequestController) currentAIRequestController.abort();
        if (currentSttRequestController) currentSttRequestController.abort();
        if (currentAIAudio) {
            currentAIAudio.onended = null;
            currentAIAudio.pause();
            currentAIAudio.currentTime = 0;
            currentAIAudio = null;
        }
        stopBrowserTts();
        if (mediaRecorder && recording) {
            try { mediaRecorder.stop(); } catch {}
        }
        recording = false;
        stopCamera();
        setAIState("idle");

        try {
            const res = await fetch("/ai/finish/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: SESSION_ID,
                    reason,
                    speech_metrics: {
                        avg_wpm: speechMetrics.avgWpm,
                        filler_count: speechMetrics.fillerCount,
                        clarity_score: speechMetrics.clarityScore,
                        pace_label: speechMetrics.paceLabel
                    },
                    face_metrics: {
                        presence_pct: faceMetrics.presencePct,
                        avg_face_size_pct: faceMetrics.avgFaceSizePct,
                        away_count: faceMetrics.awayCount,
                        expression_label: faceMetrics.expressionLabel
                    },
                    transcripts: transcriptsCache
                })
            });

            const data = await res.json();
            // show loading card (already active) then redirect
            if (feedbackLoading) {
                feedbackLoading.classList.add("active");
                feedbackLoading.setAttribute("aria-hidden", "false");
            }
            window.location.href = data.redirect;
            return true;
        } catch {
            finishingInProgress = false;
            if (endBtn) endBtn.disabled = false;
            if (feedbackLoading) {
                feedbackLoading.classList.remove("active");
                feedbackLoading.setAttribute("aria-hidden", "true");
            }
            document.body.classList.remove("feedback-loading-active");
            return false;
        }
    }

    /* ================= START / PAUSE / RESUME ================= */
    startPauseBtn.onclick = async () => {

        // ▶ START / RESUME
        if (!interviewStarted) {
            interviewStarted = true;
            startPauseBtn.textContent = "⏸ Pause";

            enableExitGuard();

            await requestMic();
            await startCamera();
            startTimer();

            if (!introCompleted) {
                const introRes = await fetch("/ai/voice/next/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, text: "__START__" })
                });

                const introData = await introRes.json();
                introCompleted = true;
                questionIndex = introData.question_index || 0;
                totalQuestions = introData.total_questions || totalQuestions;
                updateQuestionProgress();
                playAIAudio(introData.audio_url, introData.text);
            } else {
                setAIState("listening");
                startRecording();
            }
            return;
        }

        // ⏸ PAUSE
        interviewStarted = false;
        startPauseBtn.textContent = "▶ Resume";
        pauseTimer();

        disableExitGuard();

        if (currentAIAudio) currentAIAudio.pause();
        stopBrowserTts();
        if (mediaRecorder && recording) mediaRecorder.stop();

        stopCamera();
        stopMicMeter();
        setAIState("idle");
    };

    /* ================= END BUTTON ================= */
    endBtn.onclick = async () => {
        await finishInterview("manual_end");
    };

    /* ================= EXIT GUARD (ENABLE AFTER START) ================= */
    function handlePopState() {
        const needsConfirmation = interviewStarted || introCompleted || recording;
        if (!needsConfirmation) return;
        finishInterview("browser_back");
    }

    function handleBeforeUnload(e) {
        const needsConfirmation = interviewStarted || introCompleted || recording;
        if (!interviewFinished && needsConfirmation) {
            e.preventDefault();
            e.returnValue = "";
        }
    }

    function enableExitGuard() {
        history.pushState(null, "", window.location.href);
        window.addEventListener("popstate", handlePopState);
        window.addEventListener("beforeunload", handleBeforeUnload);
    }

    function disableExitGuard() {
        window.removeEventListener("popstate", handlePopState);
        window.removeEventListener("beforeunload", handleBeforeUnload);
    }

    function renderRubric() {
        if (!rubricList) return;
        const role = (window.INTERVIEW_META?.role || "").toLowerCase();
        let items = ["Technical Knowledge", "Problem Solving", "Communication", "Confidence"];

        if (role.includes("hr")) {
            items = ["Communication", "Clarity", "Culture Fit", "Confidence"];
        } else if (role.includes("frontend")) {
            items = ["UI/UX Thinking", "JavaScript", "Problem Solving", "Communication"];
        } else if (role.includes("backend")) {
            items = ["APIs & Databases", "System Design", "Problem Solving", "Communication"];
        } else if (role.includes("data")) {
            items = ["Analytics", "Statistics", "Data Handling", "Communication"];
        } else if (role.includes("devops")) {
            items = ["Infrastructure", "Reliability", "Automation", "Communication"];
        }

        rubricList.innerHTML = "";
        items.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            rubricList.appendChild(li);
        });
    }

    if (audioToggleBtn) {
        audioToggleBtn.addEventListener("click", () => {
            if (audioPaused) resumeAudio();
            else pauseAudio();
        });
    }

    if (textOnlyBtn) {
        textOnlyBtn.addEventListener("click", () => {
            if (!textOnlyModal || !textOnlyContent) return;
            textOnlyContent.textContent = lastAIText || "—";
            textOnlyModal.classList.add("show");
            textOnlyModal.setAttribute("aria-hidden", "false");
        });
    }

    // Track if a hint was just shown
    let hintJustShown = false;

    if (textOnlyClose) {
        textOnlyClose.addEventListener("click", () => {
            textOnlyModal?.classList.remove("show");
            textOnlyModal?.setAttribute("aria-hidden", "true");
            // If a hint was just shown, resume the interview flow
            if (hintJustShown) {
                hintJustShown = false;
                // Resume the answer flow or load next question if needed
                setAIState("listening");
                startRecording && startRecording();
            }
        });
    }

    if (hintBtn) {
        hintBtn.addEventListener("click", async () => {
            if (!lastAIText) return;
            if (mediaRecorder?.state === "recording") {
                suppressNextAnswer = true;
                mediaRecorder.stop();
            }
            try {
                const res = await fetchWithTimeout("/ai/voice/hint/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, text: lastAIText })
                }, 12000);
                const data = await res.json();
                if (data?.text) {
                    if (!textOnlyModal || !textOnlyContent) return;
                    textOnlyContent.textContent = data.text;
                    textOnlyModal.classList.add("show");
                    textOnlyModal.setAttribute("aria-hidden", "false");
                    hintJustShown = true;
                }
            } catch {
                showActionToast("Hint failed");
            }
        });
    }

    if (skipBtn) {
        skipBtn.addEventListener("click", async () => {
            if (mediaRecorder?.state === "recording") {
                suppressNextAnswer = true;
                mediaRecorder.stop();
            }
            try {
                const res = await fetchWithTimeout("/ai/voice/skip/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID })
                }, 12000);
                const data = await res.json();
                if (typeof data.question_index === "number") questionIndex = data.question_index;
                if (typeof data.total_questions === "number") totalQuestions = data.total_questions;
                updateQuestionProgress();
                if (data?.text) playAIAudio(data.audio_url, data.text);
            } catch {
                showActionToast("Skip failed");
            }
        });
    }


    // --- Coding question logic ---
    let currentQuestionType = null;
    let notesPerQuestion = {};
    let codePerQuestion = {};

    function isCodingQuestion(text) {
        // Simple heuristic: look for keywords, or set by backend in future
        if (!text) return false;
        const keywords = ["code", "implement", "function", "write a program", "python", "java", "c++", "algorithm"];
        return keywords.some(k => text.toLowerCase().includes(k));
    }

    function updateCodingUI(questionText) {
        const isCoding = isCodingQuestion(questionText);
        currentQuestionType = isCoding ? "coding" : "other";
        if (notesBtn) notesBtn.style.display = isCoding ? "inline-block" : "none";
        if (codeBtn) codeBtn.style.display = isCoding ? "inline-block" : "none";
        if (submitCodeBtn) submitCodeBtn.style.display = isCoding ? "inline-block" : "none";
    }

    // Show/hide notes drawer
    if (notesBtn) {
        notesBtn.addEventListener("click", () => {
            if (!notesDrawer) return;
            notesDrawer.classList.toggle("show");
            const visible = notesDrawer.classList.contains("show");
            notesDrawer.setAttribute("aria-hidden", visible ? "false" : "true");
            // Load notes for this question
            if (visible && typeof questionIndex !== "undefined") {
                notesInput.value = notesPerQuestion[questionIndex] || "";
            }
        });
    }

    if (notesClose) {
        notesClose.addEventListener("click", () => {
            notesDrawer?.classList.remove("show");
            notesDrawer?.setAttribute("aria-hidden", "true");
        });
    }

    if (notesInput) {
        notesInput.addEventListener("input", () => {
            if (typeof questionIndex !== "undefined") {
                notesPerQuestion[questionIndex] = notesInput.value;
            }
        });
    }

    // Show/hide code editor
    if (codeBtn) {
        codeBtn.addEventListener("click", () => {
            if (!codeDrawer) return;
            codeDrawer.classList.toggle("show");
            const visible = codeDrawer.classList.contains("show");
            codeDrawer.setAttribute("aria-hidden", visible ? "false" : "true");
            // Load code for this question
            if (visible && typeof questionIndex !== "undefined") {
                codeInput.value = codePerQuestion[questionIndex] || "";
            }
        });
    }

    if (codeClose) {
        codeClose.addEventListener("click", () => {
            codeDrawer?.classList.remove("show");
            codeDrawer?.setAttribute("aria-hidden", "true");
        });
    }

    if (codeInput) {
        codeInput.addEventListener("input", () => {
            if (typeof questionIndex !== "undefined") {
                codePerQuestion[questionIndex] = codeInput.value;
            }
        });
    }

    // Submit code
    if (submitCodeBtn) {
        submitCodeBtn.addEventListener("click", async () => {
            if (typeof questionIndex === "undefined" || !codeInput.value) {
                showActionToast("Write code before submitting.");
                return;
            }
            submitCodeBtn.disabled = true;
            showActionToast("Submitting code...");
            try {
                const res = await fetch("/ai/submit_code/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: SESSION_ID,
                        question_index: questionIndex,
                        code: codeInput.value
                    })
                });
                const data = await res.json();
                showActionToast(data.message || "Code submitted.");
                // Optionally show follow-up question or feedback
            } catch {
                showActionToast("Code submit failed");
            }
            submitCodeBtn.disabled = false;
        });
    }

    // Send Code: submit code and advance the interview (close editor + call next question)
    if (sendCodeBtn) {
        sendCodeBtn.addEventListener("click", async () => {
            if (typeof questionIndex === "undefined" || !codeInput.value) {
                showActionToast("Write code before sending.");
                return;
            }
            sendCodeBtn.disabled = true;
            showActionToast("Sending code...");
            try {
                // Persist locally
                codePerQuestion[questionIndex] = codeInput.value;
                // Close the code drawer UI
                if (codeDrawer) {
                    codeDrawer.classList.remove("show");
                    codeDrawer.setAttribute('aria-hidden', 'true');
                }

                // Call submit_code endpoint (evaluate/save)
                await fetch("/ai/submit_code/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, question_index: questionIndex, code: codeInput.value })
                });

                // Now send the code as the user's answer to advance the interview
                const res = await fetchWithTimeout("/ai/voice/next/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: SESSION_ID, text: codeInput.value, stt_source: 'code' })
                }, 15000);

                const data = await res.json();
                if (typeof data.question_index === "number") questionIndex = data.question_index;
                if (typeof data.total_questions === "number") totalQuestions = data.total_questions;
                updateQuestionProgress();

                if (data.phase === "complete") {
                    pendingAutoFinish = true;
                    if (feedbackLoading) {
                        feedbackLoading.classList.add("active");
                        feedbackLoading.setAttribute("aria-hidden", "false");
                    }
                    await finishInterview("auto_complete");
                    return;
                }

                if (data.use_code_editor) {
                    if (codeDrawer) {
                        codeDrawer.setAttribute('aria-hidden', 'false');
                        codeDrawer.style.display = 'block';
                    }
                    if (aiTextEl) {
                        aiTextEl.innerText = (data.text || "") + "\n\n(Please use the code editor below for this question; press Send Code when ready.)";
                    }
                    return;
                }

                playAIAudio(data.audio_url, data.text);
            } catch (e) {
                showActionToast("Send code failed");
            }
            sendCodeBtn.disabled = false;
        });
    }

    // When a new question is shown, update UI
    function onNewQuestion(questionText) {
        updateCodingUI(questionText);
    }

    // Patch: Call onNewQuestion when a new question is loaded
    // Find where playAIAudio or question text is set
    const origPlayAIAudio = window.playAIAudio;
    window.playAIAudio = function(audioUrl, text) {
        if (typeof origPlayAIAudio === "function") origPlayAIAudio(audioUrl, text);
        onNewQuestion(text);
    };

    if (notesClose) {
        notesClose.addEventListener("click", () => {
            notesDrawer?.classList.remove("show");
            notesDrawer?.setAttribute("aria-hidden", "true");
        });
    }

    if (notesInput) {
        const saved = localStorage.getItem("aiInterviewNotes");
        if (saved) notesInput.value = saved;
        notesInput.addEventListener("input", () => {
            localStorage.setItem("aiInterviewNotes", notesInput.value);
        });
    }

    if (extendBtn) {
        extendBtn.addEventListener("click", () => {
            extraAnswerTimeMs += 30000;
            showActionToast("Added 30s answer time");
        });
    }

    if (micCheckBtn) {
        micCheckBtn.addEventListener("click", async () => {
            await requestMic();
        });
    }

    window.addEventListener("online", updateNetworkStatus);
    window.addEventListener("offline", updateNetworkStatus);
    updateNetworkStatus();
    updateQuestionProgress();
    renderRubric();

    if (window.speechSynthesis) {
        const pickVoice = () => {
            const voices = window.speechSynthesis.getVoices();
            if (!voices || !voices.length) return;
            preferredVoice = voices.find(v => v.lang && v.lang.startsWith("en")) || voices[0];
        };
        pickVoice();
        window.speechSynthesis.onvoiceschanged = pickVoice;
    }
});
