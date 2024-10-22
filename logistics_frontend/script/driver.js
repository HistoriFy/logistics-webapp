const API_BASE_URL = 'https://149.102.149.102:8000/api/v1';
const WS_BASE_URL = 'wss://149.102.149.102:8000';
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

const addedBookingIds = new Set();
const currentBookingIds = new Set();

let currentOrders;
let availableOrders;
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

    fetch(`${API_BASE_URL}/driver/gps-tracking`, {
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

function updateCurrentOrdersTable(currentOrders) {
    const table = document.getElementById('currentOrdersTable').getElementsByTagName('tbody')[0];
    let existingRow = document.getElementById(`current-booking-row-${currentOrders.booking_id}`);

    if (currentOrders.status === "cancelled_by_user" || currentOrders.status === "completed") {
        console.log(`status inside cancelled if case ${currentOrders.booking_id}, ${currentOrders.status}`);
        if (existingRow) {
            existingRow.remove();
        }
        currentBookingIds.delete(currentOrders.booking_id);
        return;
    }

    console.log(`status outside cancelled if case ${currentOrders.booking_id}, ${currentOrders.status}`);

    const emptyRow = document.querySelector(`.no-current-bookings`);
    if (emptyRow) {
        emptyRow.remove();
    }

    if (!existingRow) {
        existingRow = table.insertRow();
        existingRow.id = `current-booking-row-${currentOrders.booking_id}`;
    }

    let rowHtml = '';

    rowHtml += `<td>${currentOrders.booking_id || existingRow.cells[0]?.innerText || ''}</td>`;
    rowHtml += `<td>${currentOrders.status || existingRow.cells[1]?.innerText || ''}</td>`;

    if (currentOrders.phone_number) {
        rowHtml += `<td><a href="tel:${currentOrders.phone_number}">${currentOrders.phone_number}</a></td>`;
    } else {
        rowHtml += `<td>${existingRow.cells[2]?.innerText || ''}</td>`;
    }

    rowHtml += `<td>${currentOrders.pickup_location || existingRow.cells[3]?.innerText || ''}</td>`;
    rowHtml += `<td>${currentOrders.dropoff_location || existingRow.cells[4]?.innerText || ''}</td>`;

    if (currentOrders.pickup_location && currentOrders.dropoff_location) {
        rowHtml += `<td><a href="https://www.google.com/maps/search/?api=1&origin=${currentOrders.pickup_location}&destination=${currentOrders.dropoff_location}" target="_blank" style="color: var(--text-color);">Navigate</a></td>`;
    } else {
        rowHtml += `<td>${existingRow.cells[5]?.innerHTML || ''}</td>`;
    }

    if (currentOrders.booking_id) {
        rowHtml += `<td><button class="otp-button" onclick="validateOTP(${currentOrders.booking_id})">Validate OTP</button></td>`;
        rowHtml += `<td><button class="complete-button" onclick="completeRide(${currentOrders.booking_id})">Complete Ride</button></td>`;
        rowHtml += `<td><button class="cancel-button" onclick="cancelBooking(${currentOrders.booking_id})">Cancel</button></td>`;
    } else {
        rowHtml += '<td></td><td></td><td></td>'; // Empty placeholders if no booking_id
    }

    existingRow.innerHTML = rowHtml;

    console.log(`row updated for ${currentOrders.booking_id}, ${currentOrders.status}`);

    if (!currentBookingIds.has(currentOrders.booking_id)) {
        currentBookingIds.add(currentOrders.booking_id);
    }
}

function updateAvailableOrdersTable(availableOrders) {
    const table = document.getElementById('availableOrdersTable').getElementsByTagName('tbody')[0];

    if (!availableOrders || Object.keys(availableOrders).length === 0) {
        table.innerHTML = `<tr>
            <td colspan="8" class="no-bookings">
                <div class="no-bookings-container">No available bookings</div>
            </td>
        </tr>`;    
    } else {
        if (!addedBookingIds.has(availableOrders.booking_id)) {

            if (availableOrders.status === "cancelled") {
                const rowToRemove = document.getElementById(`available-booking-row-${currentOrders.booking_id}`);
                if (rowToRemove) {
                    rowToRemove.remove();
                }
    
                addedBookingIds.delete(currentOrders.booking_id);
                return;
            }

            const emptyRow = document.querySelector(`.no-available-bookings`);
            if (emptyRow) {
                emptyRow.remove();
            }

            const row = table.insertRow();
            row.id = `available-booking-row-${availableOrders.booking_id}`;

            let rowHtml = '';

            rowHtml += `<td>${availableOrders.booking_id || ''}</td>`;
            rowHtml += `<td>${availableOrders.pickup_location || ''}</td>`;
            rowHtml += `<td>${availableOrders.dropoff_location || ''}</td>`;
            rowHtml += `<td>${availableOrders.distance ? availableOrders.distance + ' Km' : ''}</td>`;
            rowHtml += `<td>${availableOrders.estimated_cost ? '₹' + availableOrders.estimated_cost : ''}</td>`;
            
            if (availableOrders.vehicle_type_url) {
                rowHtml += `<td><img src="${availableOrders.vehicle_type_url}" alt="Vehicle Icon" class="vehicle-icon"></td>`;
            } else {
                rowHtml += '<td></td>';
            }
            
            if (availableOrders.booking_id) {
                rowHtml += `<td><button class="accept-button" onclick="acceptBooking(${availableOrders.booking_id})">Accept</button></td>`;
                rowHtml += `<td><button class="reject-button" onclick="rejectBooking(${availableOrders.booking_id})">Reject</button></td>`;
            } else {
                // placeholder for no data
                rowHtml += '<td></td><td></td>'; 
            }

            row.innerHTML = rowHtml;

            addedBookingIds.add(availableOrders.booking_id);
        }
    }
}

function updatePastOrdersTable() {
    const table = document.getElementById('pastOrdersTable').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    if (pastOrders.length === 0) {
        table.innerHTML = '<tr><td colspan="5" class="past-no-bookings">No past bookings</td></tr>';
    } else {
        pastOrders.forEach(order => {
            const row = table.insertRow();
            const readableTime = new Date(order.pickup_time).toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            });
            const fareWithSymbol = `₹${order.fare}`;
            row.innerHTML = `
                <td>${order.id}</td>
                <td>${readableTime}</td>
                <td>
                    <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(order.pickup_location)}" target="_blank" style="color: var(--text-color);">${order.pickup_location}</a>
                </td>
                <td>
                    <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(order.dropoff_location)}" target="_blank" style="color: var(--text-color);">${order.dropoff_location}</a>
                </td>
                <td>${fareWithSymbol}</td>
            `;

        });
    }
}

function toggleAvailability() {
    fetch(`${API_BASE_URL}/driver/toggle-availability/`, {
        method: 'GET',
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
            showToast(`Request accepted for booking ${bookingId}`, 'success');

            const row = document.getElementById(`available-booking-row-${bookingId}`);
            if (row) {
                row.remove();
            }

            // availableOrders = availableOrders.filter(order => order.booking_id !== bookingId);
            // updateAvailableOrdersTable();   

            // currentOrders.push(data.data.booking);
            // updateCurrentOrdersTable();
        } else {
            showToast(`Error acepting booking: ${data.error.details}`, 'error');
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
            
            const row = document.getElementById(`available-booking-row-${bookingId}`);
            if (row) {
                row.remove();
            }
            
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
                // updateCurrentOrdersTable();
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

            const rowToRemove = document.getElementById(`available-booking-row-${bookingId}`);
            if (rowToRemove) {
                rowToRemove.remove();
            }

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
                const rowToRemove = document.getElementById(`current-booking-row-${bookingId}`);
                if (rowToRemove) {
                    rowToRemove.remove();
                }
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
            console.log(data.status);
        
            const emptyRow = document.querySelector(`.no-available-bookings`);
            if (emptyRow) {
                emptyRow.remove();
            }
    
            console.log('Available orders:', data);  
            updateAvailableOrdersTable(data);
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
            console.log('Current orders:', data);
            updateCurrentOrdersTable(data);
        };

        socket.onerror = function(error) {
            showToast('Failed to fetch current orders', 'error');
            console.error('WebSocket Error:', error);
        };

        socket.onclose = function(event) {
            console.log(`Reconnecting in 5 seconds...`);
            setTimeout(() => {
                fetchCurrentOrders();
            }
            , 5000);
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

document.getElementById('refreshPastOrders').addEventListener('click', fetchPastOrders);

document.getElementById('logoutButton').addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('driverId');
    window.location.href = 'index.html';
});

document.getElementById('availabilityToggle').addEventListener('click', toggleAvailability);

document.addEventListener('DOMContentLoaded', function() {
    fetchCurrentOrders();
    fetchAvailableOrders();
    fetchPastOrders();
    // initializeWebSockets();
});