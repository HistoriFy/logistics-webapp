
        // JavaScript for toggling dark mode
        const darkModeToggle = document.getElementById('darkModeToggle');
        const body = document.body;

        // Check for saved user preference and set initial mode
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        body.classList.toggle('dark-mode', isDarkMode);
        updateDarkModeToggle(isDarkMode);

        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeToggle(isDark);
        });

        function updateDarkModeToggle(isDark) {
            darkModeToggle.textContent = isDark ? '☀️' : '🌓';
        }

        // JavaScript for handling login/register button clicks
        document.getElementById('loginBtn').addEventListener('click', function() {
            window.location.href = 'login.html';
        });

        document.getElementById('registerBtn').addEventListener('click', function() {
            window.location.href = 'register.html';
        });

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();

                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Carousel functionality
        const carouselItems = document.querySelectorAll('.carousel-item');
        const carouselImages = [
            './images/2-wheeler.jpg',
            './images/3-wheeler.jpg',
            './images/pickup.jpg',
            './images/truck.jpg'
        ];

        carouselItems.forEach((item, index) => {
            item.style.backgroundImage = `url(${carouselImages[index]})`;
        });

        let currentIndex = 0;

        function rotateCarousel() {
            carouselItems[currentIndex].classList.remove('active');
            currentIndex = (currentIndex + 1) % carouselItems.length;
            carouselItems[currentIndex].classList.add('active');
        }

        setInterval(rotateCarousel, 5000);

