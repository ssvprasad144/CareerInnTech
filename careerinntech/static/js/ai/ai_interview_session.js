document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
    const sendBtn = document.getElementById("sendBtn");

    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    async function sendMessage() {
        const userText = input.value.trim();
        if (userText === "") return;

        /* Append user message */
        const userMsg = document.createElement("div");
        userMsg.className = "message user";
        userMsg.innerText = userText;
        chatBox.appendChild(userMsg);

        input.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch("/ai/chat/", {
                method: "POST",

                // ✅ THIS IS THE MISSING FIX
                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: window.SESSION_ID,
                    message: userText
                })
            });

            if (!response.ok) {
                throw new Error("Server error");
            }

            const data = await response.json();

            /* Append AI message */
            const aiMsg = document.createElement("div");
            aiMsg.className = "message ai";
            aiMsg.innerText = data.reply;
            chatBox.appendChild(aiMsg);
            chatBox.scrollTop = chatBox.scrollHeight;

        } catch (error) {
            const errMsg = document.createElement("div");
            errMsg.className = "message ai";
            errMsg.innerText = "⚠️ Error connecting to AI backend.";
            chatBox.appendChild(errMsg);
        }
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

});
