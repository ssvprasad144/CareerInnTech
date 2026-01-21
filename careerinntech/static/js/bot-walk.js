let botWalking = false;

function startBotWalk() {
    if (botWalking) return;
    botWalking = true;

    const overlay = document.getElementById("botWalkOverlay");
    const bot = document.getElementById("botWalker");

    if (!overlay || !bot) {
        botWalking = false;
        return;
    }

    overlay.classList.remove("hidden");

    // Force clean reset
    bot.style.animation = "none";
    bot.style.transform = "translate(-120px, -50%)";
    void bot.offsetWidth;

    // Start walk
    bot.style.animation = "botWalk 8s linear forwards";

    // Redirect AFTER animation to career chat (not mock interview)
    setTimeout(() => {
        window.location.href = "/ai-chat/";
    }, 8000);
}
