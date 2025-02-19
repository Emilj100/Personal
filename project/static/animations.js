// Animationer på index siden
document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".fade-in-immediate");
    elements.forEach(element => {
        element.style.opacity = "1"; // Sikrer, at effekten fungerer selv uden scrolling
    });
});

document.addEventListener("scroll", () => {
    const sections = document.querySelectorAll(".section");
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            section.classList.add("visible");
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const slideInElements = document.querySelectorAll(".slide-in-left, .slide-in-right");

    const checkVisibility = () => {
        slideInElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            const windowHeight = window.innerHeight || document.documentElement.clientHeight;

            if (rect.top <= windowHeight - 400) {
                el.classList.add("visible");
            }
        });
    };

    // Kald funktionen ved scrolling og initialt
    window.addEventListener("scroll", checkVisibility);
    checkVisibility();
});
