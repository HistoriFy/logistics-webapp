function connectWebSocket() {
    websocket = new WebSocket(`${WS_BASE_URL}/regular_user/ws/bookings/?token=${token}`);

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
            updateCurrentOrder(data);
            break;
        case 'booking_otp_update':
            displayOTP(data);
            break;
        case 'location_update':
            console.log('Location update found:', data);
            updateDriverLocation(data);
            break;
        default:
            updateCurrentOrder(data);
            console.log('Unhandled message type:', data.type);
    }
}

function updateCurrentOrder(message) {
    console.log('Order update:', message);
    const currentOrdersList = document.getElementById('currentOrdersList');
    const orderElement = document.getElementById(`order-${message.message.id}`);
    let messageText;

    const statusMessages = {
        pending: 'Your Booking request has been received. Finding a Driver for you...',
        accepted: 'Your Booking request has been accepted. Driver is on the way to your location. Please Share OTP with the driver later to start the trip ONLY WHEN HE ARRIVES.',
        on_trip: 'Your Booking has been verified. Driver is on his way to the destination now.',
        completed: 'Your Item has been Delivered. Thank you for using our service.',
        cancelled: `Your Booking has been cancelled. Reason: ${message.message.feedback}`,
        expired: 'Your Booking request has Expired. Please Book again.'
    };

    messageText = statusMessages[message.message.status] || 'Unknown status';

    if (orderElement) {
        // Update existing order
        orderElement.querySelector('.status').textContent = `Status: ${message.message.status}`;
        if (message.message.booking_time) {
            console.log('Booking Time:', message.message.booking_time);
            orderElement.querySelector('.booking-time').textContent = `Booking Time: ${formatDate(message.message.booking_time)}`;
            orderElement.querySelector('.driver-name').textContent = `Driver: ${message.message.driver_name || 'Not assigned yet'}`;
            orderElement.querySelector('.driver-phone').textContent = `Driver Phone: ${message.message.driver_phone_number || 'Not available'}`;
            orderElement.querySelector('.driver-rating').textContent = `Driver Rating: ${message.message.driver_rating || 'Not available'}`;
        }
        orderElement.querySelector('.message').textContent = messageText;
        
        // Add feedback form if status is completed
        if (message.message.status === 'completed' && !orderElement.querySelector('.feedback-form')) {
            const feedbackForm = createFeedbackForm(message.message.id);
            orderElement.appendChild(feedbackForm);
        }
    } else {
        // Create new order element
        const newOrderElement = document.createElement('div');
        newOrderElement.id = `order-${message.message.id}`;
        newOrderElement.className = 'current-order';
        
        newOrderElement.innerHTML = `
            <h3>Booking ID: ${message.message.id}</h3>
            <p class="status">Status: ${message.message.status}</p>
            <p class="booking-time">Booking Time: ${formatDate(message.message.booking_time)}</p>
            <p class="pickup">Pickup: ${message.message.pickup_location.address}</p>
            <p class="dropoff">Dropoff: ${message.message.dropoff_location.address}</p>
            <p class="driver-name"></p>
            <p class="driver-phone"></p>
            <p class="driver-rating"></p>
            <p class="message">${messageText}</p>
            <a href="#" class="map-link" target="_blank"></a>
            <div class="otp-display"></div>
            ${['completed', 'cancelled', 'expired'].includes(message.message.status) ? '' : `<button onclick="cancelBooking(${message.message.id})" id='cancelBookingBtn'>Cancel</button>`}
        `;
        
        if (message.message.status === 'completed') {
            const feedbackForm = createFeedbackForm(message.message.id);
            newOrderElement.appendChild(feedbackForm);
        }
        
        currentOrdersList.appendChild(newOrderElement);
    }
    showToast(`Order ${message.message.id} updated: ${message.message.status}`, 'success');
}

function cancelBooking(bookingId) {
    const popup = document.getElementById('cancelBookingPopup');

    popup.style.display = 'flex';

    window.onclick = function(event) {
        if (event.target === popup) {
            popup.style.display = 'none';
        }
    };

    document.getElementById('submitCancellation').onclick = function() {
        const feedback = document.getElementById('cancellationReason').value;

        if (feedback) {
            fetch(`${API_BASE_URL}/regular_user/bookings/cancel/user/`, {
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
                } else {
                    showToast(data.error.details, 'error');
                }
                popup.style.display = 'none';
            })
            .catch(error => {
                showToast('Failed to cancel booking', 'error');
                console.error('Error:', error);
                popup.style.display = 'none';
            });
        } 
        
        else {
            alert('Please enter a reason for cancellation.');
        }
    };

    document.getElementById('cancelBookingBtn').style.display = 'none';
    document.getElementById('closePopup').onclick = function() {
        popup.style.display = 'none';
    };
}

function displayOTP(message) {
    const orderElement = document.getElementById(`order-${message.id}`);
    if (orderElement) {
        orderElement.querySelector('.otp-display').textContent = `OTP: ${message.otp}`;
        orderElement.querySelector('.status').textContent = `Status: ${message.status}`;
    }
    showToast(`OTP received for Order ${bookingId}`, 'success');
}

// Function to update the UI when a new booking is created
function addNewBookingToCurrentOrders(bookingData) {
    const currentOrdersList = document.getElementById('currentOrdersList');
    const newOrderElement = document.createElement('div');
    newOrderElement.id = `order-${bookingData.booking_id}`;
    newOrderElement.className = 'current-order';
    newOrderElement.innerHTML = `
        <h3>Booking ID: ${bookingData.booking_id}</h3>
        <p class="status">Status: ${bookingData.status}</p>
        <p class="pickup-address">Pickup: ${bookingData.pickup_location.address}</p>
        <p class="dropoff-address">Dropoff: ${bookingData.dropoff_location.address}</p>
        <p class="vehicle-type">Booking Time: ${bookingData.booking_time}</p>
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
          ${bookingData.dropoff_time ? `<p>Dropoff Time: ${new Date(bookingData.dropoff_time).toLocaleString()}</p>` : ''}
      </div>
      <div class="driver-location"></div>
  `;

  updateOrderStatus(orderElement, bookingData.status);
  
  // Initialize map link with pickup location
  updateMapLink(orderElement, bookingData.pickup_location.latitude, bookingData.pickup_location.longitude);
}

function updateDriverLocation(locationData) {
  if (locationData.booking_id) {
    const orderElement = document.getElementById(`order-${locationData.booking_id}`);
    if (orderElement) {
        orderElement.querySelector('.status').textContent = `Status: ${locationData.status}`;
        orderElement.querySelector('.map-link').href = `https://www.google.com/maps?q=${locationData.current_latitude},${locationData.current_longitude}`;
        orderElement.querySelector('.map-link').textContent = 'View Location on Map';
    }
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

function updateBookingStatus(statusData) {
  const orderElement = document.getElementById(`order-${statusData.booking_id}`);
  if (orderElement) {
      const statusElement = orderElement.querySelector('.status');
      statusElement.textContent = `Status: ${statusData.status}`;
      
      if (statusData.booking_time) {
          const timeDetails = orderElement.querySelector('.time-details');
          timeDetails.innerHTML += `<p>Booking Time: ${new Date(statusData.booking_time).toLocaleString()}</p>`;
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