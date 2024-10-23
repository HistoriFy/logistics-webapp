const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const userToggle = document.getElementById('userToggle');
const fleetToggle = document.getElementById('fleetToggle');
const driverToggle = document.getElementById('driverToggle');
const companyNameGroup = document.getElementById('companyNameGroup');
const licenseNumberGroup = document.getElementById('licenseNumberGroup');
const passwordInput = document.getElementById('password');
const passwordToggle = document.getElementById('passwordToggle');
const registrationForm = document.getElementById('registrationForm');

const API_BASE_URL = 'https://18122002.xyz/api/v1';

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

let currentUserType = 'user';

function setActiveToggle(activeToggle, userType) {
    [userToggle, fleetToggle, driverToggle].forEach(toggle => {
        toggle.classList.remove('active');
    });
    activeToggle.classList.add('active');
    currentUserType = userType;
    companyNameGroup.style.display = 'none';
    licenseNumberGroup.style.display = 'none';
    companyNameGroup.querySelector('input').required = false;
    licenseNumberGroup.querySelector('input').required = false;
}

userToggle.addEventListener('click', () => {
    setActiveToggle(userToggle, 'user');
});

fleetToggle.addEventListener('click', () => {
    setActiveToggle(fleetToggle, 'fleet_owner');
    companyNameGroup.style.display = 'block';
    companyNameGroup.querySelector('input').required = true;
});

driverToggle.addEventListener('click', () => {
    setActiveToggle(driverToggle, 'driver');
    licenseNumberGroup.style.display = 'block';
    licenseNumberGroup.querySelector('input').required = true;
});

passwordToggle.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    passwordToggle.textContent = type === 'password' ? '👁️' : '🔒';
});

registrationForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(registrationForm);
    const data = Object.fromEntries(formData.entries());

    // Remove unnecessary fields based on user type
    if (currentUserType !== 'fleet_owner') {
        delete data.company_name;
    }
    if (currentUserType !== 'driver') {
        delete data.license_number;
    }

    fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Registration successful');
            window.location.href = 'login.html';
        } else {
            alert(`Error: ${data.error.message}: ${data.error.details}`);
        }
    })
    .catch(error => console.error('Error:', error));
});