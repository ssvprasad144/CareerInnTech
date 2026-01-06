let botWalking = false;

function startBotWalk() {
    if (botWalking) return;
    botWalking = true;

    const overlay = document.getElementById("botWalkOverlay");
    const bot = document.getElementById("botWalker");
    
    overlay.classList.remove("hidden");

    // reset animation
    bot.style.animation = "none";
    bot.offsetHeight;

    // start walk
    bot.style.animation = "botWalk 7s linear forwards";

/* Redirect after walk completes */
setTimeout(() => {
    window.location.assign("/ai/");
}, 7000);


}
