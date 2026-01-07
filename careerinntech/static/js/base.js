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

    const res = await fetch("/ai/chat/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `message=${encodeURIComponent(msg)}`
    });

    const data = await res.json();
    addBotMessage(data.reply);
}

function startAIChat() {
    document.querySelector(".ai-points").style.display = "none";
    document.querySelector(".ai-start-btn").style.display = "none";
    document.getElementById("chatInput").focus();
}

function openAIBotPage() {
    window.location.href = "/ai/";
}
