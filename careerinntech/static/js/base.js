function toggleSidebar() {
    document.getElementById("profileSidebar").classList.toggle("open");
}


setTimeout(() => {
    const alerts = document.querySelector(".alert-container");
    if (alerts) alerts.style.display = "none";
}, 4000);


function toggleChatbot() {
    const chat = document.getElementById("chatbotWindow");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
}

<script>
document.addEventListener("DOMContentLoaded", function () {
    const homeLink = document.getElementById("homeLink");

    if (!homeLink) return;

    homeLink.addEventListener("click", function (e) {

        // this flag will be set after registration
        const isRegistered = "{{ request.session.is_registered|default:'False' }}";

        if (isRegistered !== "True") {
            e.preventDefault();

            alert(
                "⚠️ Please complete your registration for better mentorship and personalized guidance."
            );
        }
    });
});
</script>


