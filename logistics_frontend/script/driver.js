const API_BASE_URL = 'http://149.102.149.102:8000/api/v1';
const WS_BASE_URL = 'ws://149.102.149.102:8000';
const token = localStorage.getItem('driverToken');

document.addEventListener('DOMContentLoaded', function () {
    if (!token) {
        window.location.href = 'index.html';
    } else {
        document.body.style.display = 'block';
        console.log('Driver is authenticated');
    }   
});

const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;
const isDarkMode = localStorage.getItem('darkMode') === 'true';
body.classList.toggle('dark-mode', isDarkMode);
updateDarkModeToggle(isDarkMode);

let currentOrders = [];
let availableOrders = [];
let pastOrders = [];

const simulateToggle = document.getElementById('simulateToggle');
const statusDiv = document.getElementById('status');
let trackingInterval = null;

let userWebSocket;
let driverAvailableBookingsWebSocket;
let driverConfirmedBookingsWebSocket;

darkModeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const isDark = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    updateDarkModeToggle(isDark);
});

simulateToggle.addEventListener('change', function() {
    if (this.checked) {
        startSimulation();
    } else {
        stopSimulation();
        startTracking();
    }
});

function updateDarkModeToggle(isDark) {
    darkModeToggle.textContent = isDark ? '☀️' : '🌓';
}

function showToast(message, type) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.opacity = 1;
    setTimeout(() => {
        toast.style.opacity = 0;
    }, 3000);
}

async function startSimulation() {
    statusDiv.textContent = 'Simulation mode active';
    stopTracking();
    fetch(`${API_BASE_URL}/driver/simulate/toggle/`,{
        method: 'GET',
        headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }
    })
}

async function stopSimulation() {
    statusDiv.textContent = 'Simulation mode inactive';
    fetch(`${API_BASE_URL}/driver/simulate/toggle/`,{
        method: 'GET',
        headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }
    })
}

function startTracking() {
    if (!navigator.geolocation) {
        statusDiv.textContent = 'Geolocation is not supported by your browser.';
        return;
    }

    statusDiv.textContent = 'Requesting location permission...';

    navigator.geolocation.getCurrentPosition(
        (position) => {
            statusDiv.textContent = 'Location tracking active.';
            sendLocation();
            trackingInterval = setInterval(sendLocation, 5000);
        },
        handleError,
        {
            enableHighAccuracy: true
        }
    );
}

function stopTracking() {
    clearInterval(trackingInterval);
    trackingInterval = null;
    statusDiv.textContent = 'Location tracking inactive.';
}

function sendLocation() {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude, speed, heading } = position.coords;
            sendDataToBackend(latitude, longitude, speed, heading);
        },
        handleError,
        {
            enableHighAccuracy: true
        }
    );
}

function sendDataToBackend(latitude, longitude, speed, heading) {
    const data = {
        latitude: latitude,
        longitude: longitude,
        speed: speed,
        heading: heading
    };

    fetch('/driver/update-location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Location data sent:', data);
    })
    .catch((error) => {
        console.error('Error sending data:', error);
    });
}

function handleError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            statusDiv.textContent = 'User denied the request for Geolocation.';
            break;
        case error.POSITION_UNAVAILABLE:
            statusDiv.textContent = 'Location information is unavailable.';
            break;
        case error.TIMEOUT:
            statusDiv.textContent = 'The request to get user location timed out.';
            break;
        case error.UNKNOWN_ERROR:
            statusDiv.textContent = 'An unknown error occurred.';
            break;
    }
    console.error('Geolocation error:', error);
}

function updateCurrentOrdersTable() {
    const table = document.getElementById('currentOrdersTable').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    if (currentOrders.length === 0) {
        table.innerHTML = '<tr><td colspan="4" class="no-bookings">No current bookings</td></tr>';
    } else {
        currentOrders.forEach(order => {
            const row = table.insertRow();
            row.innerHTML = `
                <td>${order.bookin_id}</td>
                <td>${order.pickup_location}</td>
                <td>${order.dropoff_location}</td>
                <td>${order.status}</td>
                <td>
                    <button onclick="validateOTP(${order.id})">Validate OTP</button>
                    <button onclick="completeRide(${order.id})" id="completeRideBtn">Complete Ride</button>
                    <button onclick="cancelBooking(${order.id})">Cancel</button>
                </td>
            `;
        });
    }
}

function updateAvailableOrdersTable() {
    const table = document.getElementById('availableOrdersTable').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    if (availableOrders.length === 0) {
        table.innerHTML = '<tr><td colspan="4" class="no-bookings">No available bookings</td></tr>';
    } else {
        availableOrders.forEach(order => {
            const row = table.insertRow();
            row.innerHTML = `
                <td>${order.id}</td>
                <td>${order.pickup_location}</td>
                <td>${order.dropoff_location}</td>
                <td>
                    <button onclick="acceptBooking(${order.id})">Accept</button>
                    <button onclick="rejectBooking(${order.id})">Reject</button>
                </td>
            `;
        });
    }
}

function updatePastOrdersTable() {
    const table = document.getElementById('pastOrdersTable').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    if (pastOrders.length === 0) {
        table.innerHTML = '<tr><td colspan="5" class="no-bookings">No past bookings</td></tr>';
    } else {
        pastOrders.forEach(order => {
            const row = table.insertRow();
            row.innerHTML = `
                <td>${order.id}</td>
                <td>${order.pickup_time}</td>
                <td>${order.pickup_location}</td>
                <td>${order.dropoff_location}</td>
                <td>${order.fare}</td>
            `;
        });
    }
}

function toggleAvailability() {
    fetch(`${API_BASE_URL}/driver/toggle-availability/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
        } else {
            showToast(data.error.details, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to toggle availability', 'error');
        console.error('Error:', error);
    });
}

function acceptBooking(bookingId) {
    fetch(`${API_BASE_URL}/driver/accept-booking/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
            availableOrders = availableOrders.filter(order => order.id !== bookingId);
            updateAvailableOrdersTable();            
            currentOrders.push(data.data.booking);
            updateCurrentOrdersTable();
        } else {
            showToast(data.error.details, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to accept booking', 'error');
        console.error('Error:', error);
    });
}

function rejectBooking(bookingId) {
    fetch(`${API_BASE_URL}/driver/reject-booking/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
            fetchAvailableOrders();
        } else {
            showToast(data.error.details, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to reject booking', 'error');
        console.error('Error:', error);
    });
}

function validateOTP(bookingId) {
    const otp = prompt("Enter OTP:");
    if (otp) {
        fetch(`${API_BASE_URL}/driver/validate-otp/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ booking_id: bookingId, otp: otp })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.data.message, 'success');
                completeRide(bookingId);
                updateCurrentOrdersTable();
            } else {
                showToast(data.error.details, 'error');
            }
        })
        .catch(error => {
            showToast('Failed to validate OTP', 'error');
            console.error('Error:', error);
        });
    }
}

function completeRide(bookingId) {
    fetch(`${API_BASE_URL}/driver/bookings/complete/driver/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
            updateCurrentOrdersTable();
            fetchPastOrders();
        } else {
            showToast(data.error.details, 'error');
        }
    })
    .catch(error => {
        showToast('Failed to complete ride', 'error');
        console.error('Error:', error);
    });
}

function cancelBooking(bookingId) {
    const feedback = prompt("Enter cancellation reason:");
    if (feedback) {
        fetch(`${API_BASE_URL}/driver/bookings/cancel/driver/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ booking_id: bookingId, feedback: feedback })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.data.message, 'success');
                updateCurrentOrdersTable();
            } else {
                showToast(data.error.details, 'error');
            }
        })
        .catch(error => {
            showToast('Failed to cancel booking', 'error');
            console.error('Error:', error);
        });
    }
}

async function fetchAvailableOrders() {
    try {
        const socket = new WebSocket(`${WS_BASE_URL}/driver/ws/bookings/?token=${token}`);

        socket.onopen = function(event) {
            console.log("WebSocket connection established for available orders");
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
                availableOrders = data.data.available_orders;
                console.log('Available orders:', availableOrders);  
                updateAvailableOrdersTable();
        };

        socket.onerror = function(error) {
            showToast('Failed to fetch available orders', 'error');
            console.error('WebSocket Error:', error);
        };

        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.error('WebSocket connection died');
            }
        };
    } catch (error) {
        showToast('Failed to establish WebSocket connection', 'error');
        console.error('Error:', error);
    }
}

async function fetchCurrentOrders() {
    try {
        const socket = new WebSocket(`${WS_BASE_URL}/driver/ws/available_bookings/?token=${token}`);

        socket.onopen = function(event) {
            console.log("WebSocket connection established for current orders");
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
                availableOrders = data.data.available_orders;
                console.log('Current orders:', currentOrders); 
                updateCurrentOrdersTable();
        };

        socket.onerror = function(error) {
            showToast('Failed to fetch current orders', 'error');
            console.error('WebSocket Error:', error);
        };

        socket.onclose = function(event) {
            if (event.wasClean) {
                console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.error('WebSocket connection died');
            }
        };
    } catch (error) {
        showToast('Failed to establish WebSocket connection', 'error');
        console.error('Error:', error);
    }
}

async function fetchPastOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/driver/bookings/past/`, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        const data = await response.json();
        if (data.success) {
            pastOrders = data.data.past_bookings;
            updatePastOrdersTable();
        } else {
            showToast(data.error.details, 'error');
        }
    } catch (error) {
        showToast('Failed to fetch past orders', 'error');
        console.error('Error:', error);
    }
}

function initializeWebSockets() {

    driverAvailableBookingsWebSocket = new WebSocket(`ws://149.102.149.102:8000/driver/ws/available_bookings/?token=${token}`);
    
    driverAvailableBookingsWebSocket.onopen = function(e) {
        console.log("[open] Driver Available Bookings WebSocket connection established");
    };

    driverAvailableBookingsWebSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleDriverAvailableBookingsWebSocketMessage(data);
    };

    driverAvailableBookingsWebSocket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[close] Driver Available Bookings WebSocket connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Driver Available Bookings WebSocket connection died');
        }
    };

    driverAvailableBookingsWebSocket.onerror = function(error) {
        console.log(`[error] Driver Available Bookings WebSocket error: ${error.message}`);
    };

    driverConfirmedBookingsWebSocket = new WebSocket(`ws://149.102.149.102:8000/driver/ws/available_bookings/?token=${token}`);
    
    driverConfirmedBookingsWebSocket.onopen = function(e) {
        console.log("[open] Driver Confirmed Bookings WebSocket connection established");
    };

    driverConfirmedBookingsWebSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleDriverConfirmedBookingsWebSocketMessage(data);
    };

    driverConfirmedBookingsWebSocket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[close] Driver Confirmed Bookings WebSocket connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Driver Confirmed Bookings WebSocket connection died');
        }
    };

    driverConfirmedBookingsWebSocket.onerror = function(error) {
        console.log(`[error] Driver Confirmed Bookings WebSocket error: ${error.message}`);
    };
}

function handleUserWebSocketMessage(data) {
    switch (data.type) {
        case 'booking_status_update':
            updateBookingStatus(data.message);
            break;
        case 'send_otp_update':
            updateOTP(data);
            break;
        case 'location_update':
            updateDriverLocation(data);
            break;
        default:
            console.log('Unknown message type:', data.type);
    }
}

function handleDriverAvailableBookingsWebSocketMessage(data) {
    if (data.type === 'available_booking_update') {
        updateAvailableBookings(data.message);
    } else {
        console.log('Unknown message type:', data.type);
    }
}

function handleDriverConfirmedBookingsWebSocketMessage(data) {
    if (data.type === 'booking_status_update') {
        updateDriverBookingStatus(data.message);
    } else {
        console.log('Unknown message type:', data.type);
    }
}

function updateBookingStatus(message) {
    console.log('Booking status updated:', message);
    showToast(`Booking ${message.booking_id} status: ${message.status}`, 'info');
    updateCurrentOrdersTable();
}

function updateOTP(data) {
    console.log('OTP updated:', data);
    showToast(`New OTP for booking ${data.booking_id}: ${data.otp}`, 'info');
}

function updateDriverLocation(data) {
    console.log('Driver location updated:', data);
    // has to be implemented
}

function updateAvailableBookings(message) {
    console.log('Available booking update:', message);
    fetchAvailableOrders();
}

function updateDriverBookingStatus(message) {
    console.log('Driver booking status update:', message);
    updateCurrentOrdersTable();
}

document.getElementById('refreshPastOrders').addEventListener('click', fetchPastOrders);

document.getElementById('logoutButton').addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('driverId');
    window.location.href = 'index.html';
});

document.addEventListener('DOMContentLoaded', function() {
    fetchCurrentOrders();
    fetchAvailableOrders();
    fetchPastOrders();
    initializeWebSockets();
});