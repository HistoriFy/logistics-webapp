// Address autocomplete
async function initAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    const autocompleteDiv = document.getElementById(`${inputId}Autocomplete`);
    
    let debounceTimeout; // Variable to store the timeout

    input.addEventListener('input', function() {
        const query = this.value;
        
        clearTimeout(debounceTimeout);
        
        debounceTimeout = setTimeout(async function() {
            if (query.length > 2) {
                try {
                    const response = await fetch(`${API_BASE_URL}/booking/place-predictions/?query=${encodeURIComponent(query)}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
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
        }, 50); // 50 ms delay for debouncing
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
        showToast('Please select both pickup and delivery addresses from the suggestions', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/booking/price-estimation/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin_place_id: originPlaceId,
                destination_place_id: destinationPlaceId,
                place_type: document.getElementById('placeType').value
            })
        });

        const data = await response.json();
        if (data.success) {
            pickupLatitude = data.data.origin_latitude;
            pickupLongitude = data.data.origin_longitude;
            dropoffLatitude = data.data.destination_latitude;
            dropoffLongitude = data.data.destination_longitude;

            displayRideOptions(data.data);
            console.log(data.data);
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
    rideOptions.innerHTML += `
    <div class="time-dist">
        <div><strong>Total Distance:</strong> ${data.distance} kms</div>
        <div><strong>Total Time:</strong> ${Math.round(data.estimated_duration_seconds / 60)} min</div>
    </div>
    `;
    data.price_estimations.forEach(option => {
        rideOptions.innerHTML += `
            <div class="ride-option" data-vehicle-type-id="${option.vehicle_type_id}">
                <div class="ride-icon">
                <img src="${option.vehicle_image_url}" alt="${option.vehicle_type}">
                </div>
                <div class="ride-details">
                    <div class="ride-name">${option.vehicle_type}</div>
                    <div class="ride-weight">Weight: ${option.vehicle_weight} Kgs</div>
                    <div class="ride-dimensions">${option.vehicle_dimensions} </div>
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
            document.getElementById('createBookingBtn').style.display = 'block';
        });
    });
}

// Reset form after Booking
function resetForm() {
    console.log('Resetting form...');
    document.getElementById('pickupAddress').value = '';
    document.getElementById('deliveryAddress').value = '';
    document.getElementById('pickupAddressAutocomplete').innerHTML = '';
    document.getElementById('deliveryAddressAutocomplete').innerHTML = '';

    document.getElementById('paymentMethod').selectedIndex = 0;
    document.getElementById('placeType').selectedIndex = 0;

    document.getElementById('scheduledTime').value = '';
    document.getElementById('rideOptions').innerHTML = '';

    document.getElementById('newOrderForm').reset();
    document.getElementById('createBookingBtn').style.display = 'none';

    const selectedRideOption = document.querySelector('.ride-option.selected');
    if (selectedRideOption) {
        selectedRideOption.classList.remove('selected');
    }

    pickupLatitude = pickupLongitude = dropoffLatitude = dropoffLongitude = null;
    originPlaceId = destinationPlaceId = null;
}

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
    const placeType = document.getElementById('placeType').value;
    const scheduledTime = document.getElementById('scheduledTime').value;

    const requestBody = {
        vehicle_type_id: parseInt(vehicleTypeId),
        pickup_address: pickupAddress,
        dropoff_address: deliveryAddress,
        payment_method: paymentMethod,
        place_type: placeType,
        pickup_latitude: pickupLatitude,
        pickup_longitude: pickupLongitude,
        dropoff_latitude: dropoffLatitude,
        dropoff_longitude: dropoffLongitude
    };

    // Add simulatedTime to the request body if it exists and is not empty
    if (scheduledTime) {
        requestBody.scheduledTime = scheduledTime;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/booking/create-booking/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        console.log('Booking response:', data);

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

// Event listener for the "Create Booking" button
document.getElementById('createBookingBtn').addEventListener('click', createBooking);