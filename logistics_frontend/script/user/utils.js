const API_BASE_URL = 'https://18122002.xyz/api/v1';
const WS_BASE_URL = 'wss://18122002.xyz';
const token = localStorage.getItem('userToken');

let websocket;

let pickupLatitude, pickupLongitude, dropoffLatitude, dropoffLongitude;
let originPlaceId, destinationPlaceId;

let pastOrdersData = {};

//Protected functionality
document.addEventListener('DOMContentLoaded', function () {
    if (!token) {
        window.location.href = 'index.html';
    } else {
        document.body.style.display = 'block';
        console.log('User is authenticated');
    }
});

// Dark mode functionality
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
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

function formatDate(dateString) {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
        console.error('Invalid date string provided');
        return 'Invalid Date';
    }
    const formattedDateTime = date.toISOString().slice(0, 19).replace('T', ' ');
    const timezoneOffset = date.getTimezoneOffset();
    const timezoneString = (() => {
        const absOffset = Math.abs(timezoneOffset);
        const hours = Math.floor(absOffset / 60);
        const minutes = absOffset % 60;
        const sign = timezoneOffset > 0 ? '-' : '+';
        return `GMT${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    })();
    return `${formattedDateTime} ${timezoneString}`;
}

// Toast notification
function showToast(message, type) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.opacity = 1;
    setTimeout(() => {
        toast.style.opacity = 0;
    }, 3000);
}

// Tab switching
function switchTab(tabId) {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('active');
        }
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === `${tabId}Tab`) {
            content.classList.add('active');
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initAutocomplete('pickupAddress');
    initAutocomplete('deliveryAddress');

    fetchPastOrders();

    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.getAttribute('data-tab'));
        });
    });

    const newOrderForm = document.getElementById('newOrderForm');
    if (newOrderForm) {
        newOrderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await getPriceEstimation();
        });
    }

    const refreshPastOrdersButton = document.getElementById('refreshPastOrders');
    if (refreshPastOrdersButton) {
        refreshPastOrdersButton.addEventListener('click', fetchPastOrders);
    }

    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        });
    }
});

// Initial login (for demonstration purposes)
// fetch(`${API_BASE_URL}/auth/login/`, {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json'
//   },
//   body: JSON.stringify({
//     user_type: 'user',
//     email: 'test@example.com',
//     password: 'strong_password'
//   })
// })
// .then(response => response.json())
// .then(data => {
//   console.log('Login Success:', data);
//   localStorage.setItem('token', data.data.token);
//   connectWebSocket(); // Connect WebSocket after successful login
// })
// .catch(error => console.error('Login Error:', error));





// Initialize the dashboard
function initDashboard() {
    initAutocomplete('pickupAddress');
    initAutocomplete('deliveryAddress');
    fetchPastOrders();
    connectWebSocket();

    // Set up tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.getAttribute('data-tab'));
        });
    });

    // Set up event listeners
    document.getElementById('newOrderForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await getPriceEstimation();
    });

    document.getElementById('refreshPastOrders').addEventListener('click', fetchPastOrders);

    document.getElementById('logoutButton').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    });
}

// Call initDashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initDashboard);
// const style = document.createElement('style');
// style.textContent = `
//     .current-order {
//         border: 1px solid #ddd;
//         padding: 15px;
//         margin-bottom: 15px;
//         border-radius: 5px;
//         transition: all 0.3s ease;
//     }
//     .status-accepted {
//         border-left: 5px solid #ffa500;
//     }
//     .status-on-trip {
//         border-left: 5px solid #4caf50;
//     }
//     .status-completed {
//         border-left: 5px solid #2196f3;
//     }
//     .otp-display {
//         font-size: 1.2em;
//         font-weight: bold;
//         color: #e91e63;
//         margin: 10px 0;
//     }
//     .driver-location {
//         background-color: #f0f0f0;
//         padding: 10px;
//         margin-top: 10px;
//         border-radius: 5px;
//     }
// `;
// document.head.appendChild(style);
