function toggleSidebar() {
    document.getElementById("profileSidebar").classList.toggle("open");
}


setTimeout(() => {
    const alerts = document.querySelector(".alert-container");
    if (alerts) alerts.style.display = "none";
}, 3000);


function toggleChatbot() {
    const chat = document.getElementById("chatbotWindow");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
}


