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

function startSimulation() {
    statusDiv.textContent = 'Simulation mode active';
    stopTracking();
    // Call simulation API here (not provided in the API documentation)
}

function stopSimulation() {
    statusDiv.textContent = 'Simulation mode inactive';
    // Call API to stop simulation if necessary (not provided in the API documentation)
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

    fetch('http://149.102.149.102:8000/api/v1/driver/update-location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
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
                <td>${order.id}</td>
                <td>${order.pickup_location}</td>
                <td>${order.dropoff_location}</td>
                <td>${order.status}</td>
                <td>
                    <button onclick="validateOTP(${order.id})">Validate OTP</button>
                    <button onclick="completeRide(${order.id})">Complete Ride</button>
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
    fetch('http://149.102.149.102:8000/api/v1/driver/toggle-availability/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
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
    fetch('http://149.102.149.102:8000/api/v1/driver/accept-booking/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
            fetchAvailableOrders();
            fetchCurrentOrders();
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
    fetch('http://149.102.149.102:8000/api/v1/driver/reject-booking/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
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
        fetch('http://149.102.149.102:8000/api/v1/driver/validate-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ booking_id: bookingId, otp: otp })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.data.message, 'success');
                fetchCurrentOrders();
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
    fetch('http://149.102.149.102:8000/api/v1/driver/bookings/complete/driver/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.data.message, 'success');
            fetchCurrentOrders();
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
        fetch('http://149.102.149.102:8000/api/v1/driver/bookings/cancel/driver/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ booking_id: bookingId, feedback: feedback })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.data.message, 'success');
                fetchCurrentOrders();
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

async function fetchCurrentOrders() {
    try {
        const response = await fetch('http://149.102.149.102:8000/api/v1/driver/current-orders', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        });
        const data = await response.json();
        if (data.success) {
            currentOrders = data.data.current_orders;
            updateCurrentOrdersTable();
        } else {
            showToast(data.error.details, 'error');
        }
    } catch (error) {
        showToast('Failed to fetch current orders', 'error');
        console.error('Error:', error);
    }
}

async function fetchAvailableOrders() {
    try {
        const response = await fetch('http://149.102.149.102:8000/api/v1/driver/available-orders', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        });
        const data = await response.json();
        if (data.success) {
            availableOrders = data.data.available_orders;
            updateAvailableOrdersTable();
        } else {
            showToast(data.error.details, 'error');
        }
    } catch (error) {
        showToast('Failed to fetch available orders', 'error');
        console.error('Error:', error);
    }
}

async function fetchPastOrders() {
    try {
        const response = await fetch('http://149.102.149.102:8000/api/v1/driver/bookings/past/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
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
    const jwtToken = localStorage.getItem('token');

    driverAvailableBookingsWebSocket = new WebSocket(`ws://149.102.149.102:8000/driver/ws/available_bookings/?token=${jwtToken}`);
    
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

    // Driver Confirmed Bookings WebSocket
    driverConfirmedBookingsWebSocket = new WebSocket(`ws://149.102.149.102:8000/driver/ws/available_bookings/?token=${jwtToken}`);
    
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
    fetchCurrentOrders();
}

function updateOTP(data) {
    console.log('OTP updated:', data);
    showToast(`New OTP for booking ${data.booking_id}: ${data.otp}`, 'info');
}

function updateDriverLocation(data) {
    console.log('Driver location updated:', data);
    // You might want to update a map here if you're using one
}

function updateAvailableBookings(message) {
    console.log('Available booking update:', message);
    fetchAvailableOrders();
}

function updateDriverBookingStatus(message) {
    console.log('Driver booking status update:', message);
    fetchCurrentOrders();
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