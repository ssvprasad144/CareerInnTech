document.querySelector(".cta-btn").addEventListener("click", () => {
    window.location.href = "/signup"; // change later if needed
});
const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("show");
});
