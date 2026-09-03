/**
 * Harsha Karimikonda Portfolio - Main Controller
 * Interactions: Card Spotlight Glow, Dynamic Typing, Project Filters, Copy-to-Clipboard, Theme Switching
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // 2. Mouse Spotlight Tracking on Cards
    const spotlightCards = document.querySelectorAll('.spotlight-card, .metric-card, .featured-flagship-pill');
    spotlightCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
        card.addEventListener('mouseleave', () => {
            card.style.setProperty('--mouse-x', '-1000px');
            card.style.setProperty('--mouse-y', '-1000px');
        });
    });

    // 3. Theme Toggle (Dark / Light)
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        themeToggleBtn.innerHTML = theme === 'dark'
            ? '<i data-lucide="sun"></i>'
            : '<i data-lucide="moon"></i>';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    // 4. Typing Animation
    const typedTextEl = document.getElementById('typed-text');
    if (typedTextEl) {
        const phrases = [
            "High-Throughput ML Systems.",
            "Scalable Distributed Backends.",
            "Low-Latency LLM Serving Planes.",
            "Deep Learning & Computer Vision.",
            "Open-Source AI & RAG Tools."
        ];
        let phraseIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        const typeSpeed = 75;
        const deleteSpeed = 40;
        const pauseDelay = 1800;

        function typeLoop() {
            const currentPhrase = phrases[phraseIndex];
            
            if (isDeleting) {
                typedTextEl.textContent = currentPhrase.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typedTextEl.textContent = currentPhrase.substring(0, charIndex + 1);
                charIndex++;
            }

            if (!isDeleting && charIndex === currentPhrase.length) {
                isDeleting = true;
                setTimeout(typeLoop, pauseDelay);
                return;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                phraseIndex = (phraseIndex + 1) % phrases.length;
                setTimeout(typeLoop, 400);
                return;
            }

            const currentSpeed = isDeleting ? deleteSpeed : typeSpeed;
            setTimeout(typeLoop, currentSpeed);
        }

        setTimeout(typeLoop, 800);
    }

    // 5. Project Category Filtering
    const filterPills = document.querySelectorAll('.filter-pill');
    const projectCards = document.querySelectorAll('.project-card');

    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const filter = pill.getAttribute('data-filter');

            projectCards.forEach(card => {
                const category = card.getAttribute('data-category');
                card.style.opacity = '0';
                card.style.transform = 'translateY(12px) scale(0.98)';

                setTimeout(() => {
                    if (filter === 'all' || category === filter) {
                        card.style.display = 'flex';
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0) scale(1)';
                        }, 50);
                    } else {
                        card.style.display = 'none';
                    }
                }, 200);
            });
        });
    });

    // 6. Quick Copy Email with Toast
    const copyEmailBtn = document.getElementById('copy-email-btn');
    const toastNotice = document.getElementById('toast-notice');

    if (copyEmailBtn) {
        copyEmailBtn.addEventListener('click', () => {
            const email = "harshakarimikonda22@gmail.com";
            navigator.clipboard.writeText(email).then(() => {
                showToast("Copied harshakarimikonda22@gmail.com to clipboard!");
            }).catch(() => {
                showToast("Failed to copy. Email: harshakarimikonda22@gmail.com");
            });
        });
    }

    function showToast(message) {
        if (!toastNotice) return;
        toastNotice.querySelector('.toast-msg').textContent = message;
        toastNotice.classList.add('show');
        setTimeout(() => {
            toastNotice.classList.remove('show');
        }, 3200);
    }

    // 7. Contact Form Submission Handler (Live via FormSubmit.co)
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalContent = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Sending Message...</span>';

            const formData = new FormData(contactForm);
            const payload = {
                name: formData.get('name'),
                email: formData.get('email'),
                _subject: `[Portfolio Inquiry] ${formData.get('subject')}`,
                message: formData.get('message'),
                _honey: formData.get('_honey') || '',
                _template: 'table',
                _captcha: 'false'
            };

            fetch('https://formsubmit.co/ajax/harshakarimikonda22@gmail.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                showToast("Message sent successfully! It has been delivered to my inbox.");
                contactForm.reset();
            })
            .catch(err => {
                showToast("Direct send error. Please email harshakarimikonda22@gmail.com directly!");
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalContent;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            });
        });
    }

    // 8. Navbar Scroll Spy
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let currentSectionId = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            const sectionHeight = section.offsetHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                currentSectionId = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });
    });

    // 9. Mobile Menu Navigation Toggle
    const mobileToggleBtn = document.getElementById('mobile-toggle');
    const navLinksContainer = document.getElementById('nav-links');
    if (mobileToggleBtn && navLinksContainer) {
        mobileToggleBtn.addEventListener('click', () => {
            navLinksContainer.classList.toggle('mobile-open');
            const isOpen = navLinksContainer.classList.contains('mobile-open');
            mobileToggleBtn.innerHTML = isOpen
                ? '<i data-lucide="x"></i>'
                : '<i data-lucide="menu"></i>';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        });

        // Close menu when clicking any nav link
        navLinksContainer.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navLinksContainer.classList.remove('mobile-open');
                mobileToggleBtn.innerHTML = '<i data-lucide="menu"></i>';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            });
        });
    }
});
