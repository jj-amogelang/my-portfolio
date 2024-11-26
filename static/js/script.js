document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.nav-button');
    const sections = document.querySelectorAll('.content-section');
    const scrollLeftButton = document.getElementById('scroll-left');
    const scrollRightButton = document.getElementById('scroll-right');
    const projectsContainer = document.querySelector('.projects-container');
    const projectCards = document.querySelectorAll('.project-card');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.getAttribute('data-target');

            // Hide all sections
            sections.forEach(section => {
                section.classList.remove('active');
            });

            // Show the target section
            document.getElementById(target).classList.add('active');
        });
    });

    scrollLeftButton.addEventListener('click', () => {
        projectsContainer.scrollBy({
            left: -300, // Adjust this value for scroll distance
            behavior: 'smooth'
        });
    });

    scrollRightButton.addEventListener('click', () => {
        projectsContainer.scrollBy({
            left: 300, // Adjust this value for scroll distance
            behavior: 'smooth'
        });
    });

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    projectCards.forEach(card => {
        observer.observe(card);
    });

    const container = document.getElementById('projects-container');
    const leftButton = document.getElementById('scroll-left');
    const rightButton = document.getElementById('scroll-right');
    const cards = document.querySelectorAll('.project-card');

    const updateVisibility = () => {
        const containerRect = container.getBoundingClientRect();
        cards.forEach(card => {
            const cardRect = card.getBoundingClientRect();
            if (cardRect.right > containerRect.left && cardRect.left < containerRect.right) {
                card.classList.add('visible');
            } else {
                card.classList.remove('visible');
            }
        });
    };

    leftButton.addEventListener('click', () => {
        container.scrollBy({ left: -300, behavior: 'smooth' });
    });

    rightButton.addEventListener('click', () => {
        container.scrollBy({ left: 300, behavior: 'smooth' });
    });

    container.addEventListener('scroll', updateVisibility);

    // Initial visibility check
    updateVisibility();
});