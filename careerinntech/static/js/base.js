function toggleSidebar() {
    document.getElementById("profileSidebar").classList.toggle("open");
}

// Auto-hide alerts after 4 seconds
document.addEventListener("DOMContentLoaded", () => {
    const alertContainer = document.querySelector(".alert-container");

    if (alertContainer) {
        setTimeout(() => {
            alertContainer.style.opacity = "0";
            alertContainer.style.transition = "opacity 0.5s ease";

            setTimeout(() => {
                alertContainer.remove();
            }, 500);
        }, 4000);
    }
}); // ✅ THIS WAS MISSING


function toggleChatbot() {
    const chat = document.getElementById("chatbotWindow");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (!msg) return;

    addUserMessage(msg);
    input.value = "";

    // Use career guidance AI endpoint (core.openai_ai_chat)
    const res = await fetch("/api/ai-chat/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: msg })
    });

    const data = await res.json();
    if (data.reply) addBotMessage(data.reply);
    else addBotMessage("⚠️ AI error");
}

function startAIChat() {
    document.querySelector(".ai-points").style.display = "none";
    document.querySelector(".ai-start-btn").style.display = "none";
    document.getElementById("chatInput").focus();
}

function openAIBotPage() {
    // Open the career guidance AI chat page (not the mock interview)
    window.location.href = "/ai-chat/";
}
