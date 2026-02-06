document.addEventListener("DOMContentLoaded", () => {
    console.log("UI.js loaded, initializing hover effects");
    // Hover scaling and popup for cards
    const cards = document.querySelectorAll(".evidence-card, .timeline-block, .glass-card, .card");
    console.log("Found cards:", cards.length);
    cards.forEach(card => {
        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'card-popup';
        popup.style.position = 'absolute';
        popup.style.background = 'rgba(0, 0, 0, 0.8)';
        popup.style.color = '#fff';
        popup.style.padding = '10px';
        popup.style.borderRadius = '5px';
        popup.style.fontSize = '12px';
        popup.style.pointerEvents = 'none';
        popup.style.zIndex = '1000';
        popup.style.display = 'none';
        document.body.appendChild(popup);

        card.addEventListener("mouseenter", (e) => {
            card.style.transform = "scale(1.05)";
            card.style.transition = "0.3s";
            card.style.boxShadow = "0 8px 25px rgba(0, 0, 0, 0.3)";

            // Show popup with card title
            const title = card.querySelector('h2') ? card.querySelector('h2').textContent : 'Card';
            popup.textContent = title;
            popup.style.display = 'block';
            popup.style.left = (e.pageX + 10) + 'px';
            popup.style.top = (e.pageY + 10) + 'px';
        });

        card.addEventListener("mousemove", (e) => {
            if (popup.style.display === 'block') {
                popup.style.left = (e.pageX + 10) + 'px';
                popup.style.top = (e.pageY + 10) + 'px';
            }
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "scale(1)";
            card.style.boxShadow = "";
            popup.style.display = 'none';
        });
    });

    // Smooth scroll to sections
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
