const darkModeToggle = document.getElementById('darkModeToggle');
        const body = document.body;
        const userToggle = document.getElementById('userToggle');
        const fleetToggle = document.getElementById('fleetToggle');
        const driverToggle = document.getElementById('driverToggle');
        const passwordInput = document.getElementById('password');
        const passwordToggle = document.getElementById('passwordToggle');
        const loginForm = document.getElementById('loginForm');

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

        function setActiveToggle(activeToggle) {
            [userToggle, fleetToggle, driverToggle].forEach(toggle => {
                toggle.classList.remove('active');
            });
            activeToggle.classList.add('active');
        }

        userToggle.addEventListener('click', () => setActiveToggle(userToggle));
        fleetToggle.addEventListener('click', () => setActiveToggle(fleetToggle));
        driverToggle.addEventListener('click', () => setActiveToggle(driverToggle));

        passwordToggle.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            passwordToggle.textContent = type === 'password' ? '👁️' : '🔒';
        });

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const inputData = Object.fromEntries(formData.entries());

            // Add user type to the data
            if (userToggle.classList.contains('active')) {
                inputData.user_type = 'user';
            } else if (fleetToggle.classList.contains('active')) {
                inputData.user_type = 'fleet_owner';
            } else if (driverToggle.classList.contains('active')) {
                inputData.user_type = 'driver';
            }
            
            fetch('http://149.102.149.102:8000/api/v1/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(inputData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Login successful');

                    localStorage.setItem('token', data.data.token);

                    if (inputData.user_type === 'user') {
                        window.location.href = 'user-dashboard.html'; // Change to your user dashboard
                    } else if (inputData.user_type === 'fleet_owner') {
                        window.location.href = 'fleet-owner-dashboard.html'; // Change to your fleet owner dashboard
                    } else if (inputData.user_type === 'driver') {
                        window.location.href = 'driver-dashboard.html'; // Change to your driver dashboard
                    }

                } else {
                    alert(`Error: ${data.error.message}: ${data.error.details}`);
                }
            })
            .catch(error => console.error('Error:', error));
        });