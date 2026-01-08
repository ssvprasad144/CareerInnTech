const cards = document.querySelectorAll(".select-card");
const proceedBtn = document.getElementById("proceedBtn");

let selectedType = null;

cards.forEach(card => {
    card.addEventListener("click", () => {
        cards.forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");

        selectedType = card.dataset.type;
        proceedBtn.disabled = false;
    });
});

proceedBtn.addEventListener("click", () => {
    if (!selectedType) return;

    // Store selection (temporary – later backend session)
    sessionStorage.setItem("interview_type", selectedType);

    window.location.href = "/ai/ai-interview-session/";
});
