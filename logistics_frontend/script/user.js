const API_BASE_URL = 'http://149.102.149.102:8000/api/v1';
let websocket;

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

// WebSocket connection
function connectWebSocket() {
    const token = localStorage.getItem('token');
    websocket = new WebSocket(`ws://149.102.149.102:8000/regular_user/ws/bookings/?token=${token}`);

    websocket.onopen = () => {
        console.log('WebSocket connection established');
    };

    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after a delay
        setTimeout(connectWebSocket, 5000);
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'booking_status_update':
            updateCurrentOrder(data.message);
            break;
        case 'send_otp_update':
            displayOTP(data.otp, data.booking_id);
            break;
        case 'location_update':
            updateDriverLocation(data);
            break;
        default:
            console.log('Unhandled message type:', data.type);
    }
}

function updateCurrentOrder(message) {
    const currentOrdersList = document.getElementById('currentOrdersList');
    const orderElement = document.getElementById(`order-${message.booking_id}`);

    if (orderElement) {
        // Update existing order
        orderElement.querySelector('.status').textContent = `Status: ${message.status}`;
        if (message.pickup_time) {
            orderElement.querySelector('.pickup-time').textContent = `Pickup Time: ${message.pickup_time}`;
        }
        if (message.message) {
            orderElement.querySelector('.message').textContent = message.message;
        }
    } else {
        // Create new order element
        const newOrderElement = document.createElement('div');
        newOrderElement.id = `order-${message.booking_id}`;
        newOrderElement.className = 'current-order';
        newOrderElement.innerHTML = `
            <h3>Booking ID: ${message.booking_id}</h3>
            <p class="status">Status: ${message.status}</p>
            <p class="pickup-time">Pickup Time: ${message.pickup_time || 'N/A'}</p>
            <p class="message">${message.message || ''}</p>
            <div class="otp-display"></div>
        `;
        currentOrdersList.appendChild(newOrderElement);
    }

    showToast(`Order ${message.booking_id} updated: ${message.status}`, 'success');
}

function displayOTP(otp, bookingId) {
    const orderElement = document.getElementById(`order-${bookingId}`);
    if (orderElement) {
        const otpDisplay = orderElement.querySelector('.otp-display');
        otpDisplay.textContent = `OTP: ${otp}`;
    }
    showToast(`OTP received for Order ${bookingId}`, 'success');
}

function updateDriverLocation(data) {
    const orderElement = document.getElementById(`order-${data.booking_id}`);
    if (orderElement) {
        const locationElement = orderElement.querySelector('.driver-location') || document.createElement('p');
        locationElement.className = 'driver-location';
        locationElement.textContent = `Driver Location: Lat ${data.current_latitude}, Long ${data.current_longitude}`;
        orderElement.appendChild(locationElement);
    }
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

// Fetch past orders
async function fetchPastOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/booking/fetch-all-past-bookings/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Accept': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            const pastOrderTable = document.getElementById('pastOrderTable').getElementsByTagName('tbody')[0];
            pastOrderTable.innerHTML = '';
            data.data.forEach(order => {
                const row = pastOrderTable.insertRow();
                row.innerHTML = `
                    <td>${order.booking_id}</td>
                    <td>${new Date(order.scheduled_time).toLocaleString()}</td>
                    <td>${order.status}</td>
                    <td>${order.estimated_cost} INR</td>
                    <td><button onclick="viewPastOrderDetails(${order.booking_id})">View Details</button></td>
                `;
            });
        } else {
            showToast(data.error.message || 'Failed to fetch past orders', 'error');
        }
    } catch (error) {
        showToast('Failed to fetch past orders', 'error');
    }
}

async function viewPastOrderDetails(orderId) {
    showToast(`Viewing details for order ${orderId}`, 'success');
    // Implement the logic to fetch and display order details
}

// Address autocomplete
let originPlaceId, destinationPlaceId;

async function initAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    const autocompleteDiv = document.getElementById(`${inputId}Autocomplete`);
    
    input.addEventListener('input', async function() {
        const query = this.value;
        if (query.length > 2) {
            try {
                const response = await fetch(`${API_BASE_URL}/booking/place-predictions/?query=${encodeURIComponent(query)}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Accept': 'application/json'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    showSuggestions(data.data.predictions, autocompleteDiv, input, inputId);
                } else {
                    console.error('Failed to fetch address suggestions:', data.error);
                    autocompleteDiv.style.display = 'none';
                }
            } catch (error) {
                console.error('Failed to fetch address suggestions:', error);
                autocompleteDiv.style.display = 'none';
            }
        } else {
            autocompleteDiv.innerHTML = '';
            autocompleteDiv.style.display = 'none';
        }
    });

    document.addEventListener('click', function(e) {
        if (autocompleteDiv && e.target !== input && !autocompleteDiv.contains(e.target)) {
            autocompleteDiv.style.display = 'none';
        }
    });
}

function showSuggestions(suggestions, autocompleteDiv, input, inputId) {
    autocompleteDiv.innerHTML = '';
    if (suggestions && suggestions.length > 0) {
        autocompleteDiv.style.display = 'block';
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.innerHTML = suggestion.description;
            div.addEventListener('click', function() {
                input.value = suggestion.description;
                if (inputId === 'pickupAddress') {
                    originPlaceId = suggestion.place_id;
                } else if (inputId === 'deliveryAddress') {
                    destinationPlaceId = suggestion.place_id;
                }
                autocompleteDiv.style.display = 'none';
            });
            autocompleteDiv.appendChild(div);
        });
    } else {
        autocompleteDiv.style.display = 'none';
    }
}

// Price estimation
async function getPriceEstimation() {
    if (!originPlaceId || !destinationPlaceId) {
        showToast('Please select both pickup and delivery addresses', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/booking/price-estimation/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin_place_id: originPlaceId,
                destination_place_id: destinationPlaceId,
                place_type: 'city'
            })
        });

        const data = await response.json();
        if (data.success) {
            displayRideOptions(data.data);
        } else {
            showToast(data.error.message || 'Failed to get price estimation', 'error');
        }
    } catch (error) {
        showToast('Failed to get price estimation', 'error');
    }
}

function displayRideOptions(data) {
    const rideOptions = document.getElementById('rideOptions');
    rideOptions.innerHTML = '';
    data.price_estimations.forEach(option => {
        rideOptions.innerHTML += `
            <div class="ride-option" data-vehicle-type-id="${option.vehicle_type_id}">
                <div class="ride-icon">🚗</div>
                <div class="ride-details">
                    <div class="ride-name">${option.vehicle_type}</div>
                    <div class="ride-eta">ETA: ${Math.round(data.estimated_duration_seconds / 60)} min</div>
                </div>
                <div class="ride-price">${option.estimated_cost} ${option.currency}</div>
            </div>
        `;
    });
    rideOptions.style.display = 'block';

    const rideOptionElements = document.querySelectorAll('.ride-option');
    rideOptionElements.forEach(option => {
        option.addEventListener('click', () => {
            rideOptionElements.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
            showToast('Ride option selected', 'success');
        });
    });
}

// Create booking
async function createBooking() {
    const selectedRideOption = document.querySelector('.ride-option.selected');
    if (!selectedRideOption) {
        showToast('Please select a ride option', 'error');
        return;
    }

    const vehicleTypeId = selectedRideOption.getAttribute('data-vehicle-type-id');
    const pickupAddress = document.getElementById('pickupAddress').value;
    const deliveryAddress = document.getElementById('deliveryAddress').value;
    const paymentMethod = document.getElementById('paymentMethod').value;

    try {
        const response = await fetch(`${API_BASE_URL}/booking/create-booking/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vehicle_type_id: parseInt(vehicleTypeId),
                pickup_address: pickupAddress,
                dropoff_address: deliveryAddress,
                payment_method: paymentMethod,
                pickup_latitude: 0,
                pickup_longitude: 0,
                dropoff_latitude: 0,
                dropoff_longitude: 0
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(`Booking created successfully. Booking ID: ${data.data.booking_id}`, 'success');
            resetForm();
            switchTab('currentOrders');
        } else {
            showToast(data.error.message || 'Failed to create booking', 'error');
        }
    } catch (error) {
        showToast('Failed to create booking', 'error');
    }
}

function resetForm() {
    document.getElementById('pickupAddress').value = '';
    document.getElementById('deliveryAddress').value = '';
    document.getElementById('paymentMethod').selectedIndex = 0;
    document.getElementById('rideOptions').innerHTML = '';
    document.getElementById('rideOptions').style.display = 'none';
    originPlaceId = null;
    destinationPlaceId = null;
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
// ... (previous code remains unchanged) ...

// Initial login (for demonstration purposes)
fetch('http://149.102.149.102:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_type: 'user',
    email: 'test@example.com',
    password: 'strong_password'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Login Success:', data);
  localStorage.setItem('token', data.data.token);
  connectWebSocket(); // Connect WebSocket after successful login
})
.catch(error => console.error('Login Error:', error));

// Function to create a new booking
async function createBooking() {
    const selectedRideOption = document.querySelector('.ride-option.selected');
    if (!selectedRideOption) {
        showToast('Please select a ride option', 'error');
        return;
    }

    const vehicleTypeId = selectedRideOption.getAttribute('data-vehicle-type-id');
    const pickupAddress = document.getElementById('pickupAddress').value;
    const deliveryAddress = document.getElementById('deliveryAddress').value;
    const paymentMethod = document.getElementById('paymentMethod').value;

    try {
        const response = await fetch(`${API_BASE_URL}/booking/create-booking/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vehicle_type_id: parseInt(vehicleTypeId),
                pickup_address: pickupAddress,
                dropoff_address: deliveryAddress,
                payment_method: paymentMethod,
                pickup_latitude: 0,
                pickup_longitude: 0,
                dropoff_latitude: 0,
                dropoff_longitude: 0
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(`Booking created successfully. Booking ID: ${data.data.booking_id}`, 'success');
            resetForm();
            switchTab('currentOrders');
        } else {
            showToast(data.error.message || 'Failed to create booking', 'error');
        }
    } catch (error) {
        showToast('Failed to create booking', 'error');
    }
}

// Function to reset the form after creating a booking
function resetForm() {
    document.getElementById('pickupAddress').value = '';
    document.getElementById('deliveryAddress').value = '';
    document.getElementById('paymentMethod').selectedIndex = 0;
    document.getElementById('rideOptions').innerHTML = '';
    document.getElementById('rideOptions').style.display = 'none';
    originPlaceId = null;
    destinationPlaceId = null;
}

// Event listener for the "Create Booking" button
document.getElementById('createBookingBtn').addEventListener('click', createBooking);

// Function to update the UI when a new booking is created
function addNewBookingToCurrentOrders(bookingData) {
    const currentOrdersList = document.getElementById('currentOrdersList');
    const newOrderElement = document.createElement('div');
    newOrderElement.id = `order-${bookingData.booking_id}`;
    newOrderElement.className = 'current-order';
    newOrderElement.innerHTML = `
        <h3>Booking ID: ${bookingData.booking_id}</h3>
        <p class="status">Status: ${bookingData.status}</p>
        <p class="pickup-address">Pickup: ${bookingData.pickup_address}</p>
        <p class="dropoff-address">Dropoff: ${bookingData.dropoff_address}</p>
        <p class="vehicle-type">Vehicle: ${bookingData.vehicle_type}</p>
        <div class="otp-display"></div>
    `;
    currentOrdersList.appendChild(newOrderElement);
}

// Function to handle real-time updates for current orders
function handleRealTimeUpdate(update) {
    const orderElement = document.getElementById(`order-${update.booking_id}`);
    if (orderElement) {
        orderElement.querySelector('.status').textContent = `Status: ${update.status}`;
        if (update.driver_location) {
            const locationElement = orderElement.querySelector('.driver-location') || document.createElement('p');
            locationElement.className = 'driver-location';
            locationElement.textContent = `Driver Location: Lat ${update.driver_location.latitude}, Long ${update.driver_location.longitude}`;
            orderElement.appendChild(locationElement);
        }
        if (update.otp) {
            orderElement.querySelector('.otp-display').textContent = `OTP: ${update.otp} (share only when you want to start the trip)`;
        }
    }
}

function handleWebSocketMessage(data) {
  console.log('Received WebSocket message:', data);
  if (data.id) {
      updateBookingDetails(data);
  } else if (data.type === 'location_update') {
      updateDriverLocation(data);
  } else if (data.otp) {
      displayOTP(data.otp, data.id);
  } else if (data.status) {
      updateBookingStatus(data);
  }
}
function updateBookingDetails(bookingData) {
  const currentOrdersList = document.getElementById('currentOrdersList');
  let orderElement = document.getElementById(`order-${bookingData.id}`);

  if (!orderElement) {
      orderElement = document.createElement('div');
      orderElement.id = `order-${bookingData.id}`;
      orderElement.className = 'current-order';
      currentOrdersList.appendChild(orderElement);
  }

  orderElement.innerHTML = `
      <h3>Booking ID: ${bookingData.id}</h3>
      <a href="#" class="map-link" target="_blank">View on Map</a>
      <p class="status">Status: ${bookingData.status}</p>
      <p class="pickup">Pickup: ${bookingData.pickup_location.address}</p>
      <p class="dropoff">Dropoff: ${bookingData.dropoff_location.address}</p>
      <p class="estimated-cost">Estimated Cost: ${bookingData.estimated_cost}</p>
      <p class="distance">Distance: ${bookingData.distance} km</p>
      <p class="duration">Estimated Duration: ${bookingData.estimated_duration}</p>
      <p class="payment-method">Payment Method: ${bookingData.payment_method}</p>
      <div class="otp-display">${bookingData.otp ? `OTP: ${bookingData.otp}` : ''}</div>
      <div class="time-details">
          <p>Booking Time: ${new Date(bookingData.booking_time).toLocaleString()}</p>
          ${bookingData.pickup_time ? `<p>Pickup Time: ${new Date(bookingData.pickup_time).toLocaleString()}</p>` : ''}
          ${bookingData.dropoff_time ? `<p>Dropoff Time: ${new Date(bookingData.dropoff_time).toLocaleString()}</p>` : ''}
      </div>
      <div class="driver-location"></div>
  `;

  updateOrderStatus(orderElement, bookingData.status);
  
  // Initialize map link with pickup location
  updateMapLink(orderElement, bookingData.pickup_location.latitude, bookingData.pickup_location.longitude);
}

function updateDriverLocation(locationData) {
  const orderElement = document.getElementById(`order-${locationData.booking_id}`);
  if (orderElement) {
      const locationElement = orderElement.querySelector('.driver-location');
      locationElement.innerHTML = `
          <p>Driver Location: Lat ${locationData.current_latitude}, Long ${locationData.current_longitude}</p>
          <p>Status: ${formatDriverStatus(locationData.status)}</p>
      `;

      // Update map link with new driver location
      updateMapLink(orderElement, locationData.current_latitude, locationData.current_longitude);
  }
}

function updateMapLink(orderElement, latitude, longitude) {
  const mapLink = orderElement.querySelector('.map-link');
  if (mapLink) {
      mapLink.href = `https://www.google.com/maps?q=${latitude},${longitude}`;
  }
}

function formatDriverStatus(status) {
  const statusMap = {
      'en_route_to_pickup': 'En route to pickup',
      'at_pickup': 'At pickup location',
      'on_trip': 'On trip',
      'at_dropoff': 'At dropoff location'
  };
  return statusMap[status] || status;
}

function displayOTP(otp, bookingId) {
  const orderElement = document.getElementById(`order-${bookingId}`);
  if (orderElement) {
      const otpDisplay = orderElement.querySelector('.otp-display');
      otpDisplay.textContent = `OTP: ${otp}`;
      showToast(`OTP received for Order ${bookingId}: ${otp}`, 'success');
  }
}

function updateBookingStatus(statusData) {
  const orderElement = document.getElementById(`order-${statusData.booking_id}`);
  if (orderElement) {
      const statusElement = orderElement.querySelector('.status');
      statusElement.textContent = `Status: ${statusData.status}`;
      
      if (statusData.pickup_time) {
          const timeDetails = orderElement.querySelector('.time-details');
          timeDetails.innerHTML += `<p>Pickup Time: ${new Date(statusData.pickup_time).toLocaleString()}</p>`;
      }

      if (statusData.message) {
          showToast(statusData.message, 'info');
      }

      updateOrderStatus(orderElement, statusData.status);
  }
}

function updateOrderStatus(orderElement, status) {
  orderElement.classList.remove('status-accepted', 'status-on-trip', 'status-completed');
  orderElement.classList.add(`status-${status.replace('_', '-')}`);
}

// Function to periodically check WebSocket connection and reconnect if necessary
function checkWebSocketConnection() {
    if (!websocket || websocket.readyState === WebSocket.CLOSED) {
        console.log('WebSocket is closed. Attempting to reconnect...');
        connectWebSocket();
    }
}

// Set up periodic WebSocket connection check
setInterval(checkWebSocketConnection, 30000); // Check every 30 seconds

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
const style = document.createElement('style');
style.textContent = `
    .current-order {
        border: 1px solid #ddd;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .status-accepted {
        border-left: 5px solid #ffa500;
    }
    .status-on-trip {
        border-left: 5px solid #4caf50;
    }
    .status-completed {
        border-left: 5px solid #2196f3;
    }
    .otp-display {
        font-size: 1.2em;
        font-weight: bold;
        color: #e91e63;
        margin: 10px 0;
    }
    .driver-location {
        background-color: #f0f0f0;
        padding: 10px;
        margin-top: 10px;
        border-radius: 5px;
    }
`;
document.head.appendChild(style);
