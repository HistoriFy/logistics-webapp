// Fetch past orders
async function fetchPastOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/booking/fetch-all-past-bookings/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            const pastOrderTable = document.getElementById('pastOrderTable').getElementsByTagName('tbody')[0];
            pastOrderTable.innerHTML = '';
            data.data.forEach(order => {
                pastOrdersData[order.booking_id] = order;
                const readableTime = new Date(order.created_at).toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                });

                const estimatedCostWithSymbol = `₹${order.estimated_cost}`;

                const row = pastOrderTable.insertRow();
                row.innerHTML = `
                    <td>${order.booking_id}</td>
                    <td>${readableTime}</td>
                    <td>${order.status}</td>
                    <td>${estimatedCostWithSymbol}</td>
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
    const order = pastOrdersData[orderId];
    if (!order) {
        showToast('Order not found', 'error');
        return;
    }

    // console.log('Order details:', order.vehicle_type, order.pickup_address, order.dropoff_address, order.status, order.distance, order.payment_method, order.estimated_cost, order.created_at);

    const detailedInfo = `
        <p>Vehicle Type: ${order.vehicle_type}</p>
        <p>Pickup Address: ${order.pickup_address}</p>
        <p>Dropoff Address: ${order.dropoff_address}</p>
        <p>Status: ${order.status}</p>
        <p>Distance: ${order.distance} km</p>
        <p>Payment Method: ${order.payment_method}</p>
        <p>Estimated Cost: ${order.estimated_cost} INR</p>
        <p>Created At: ${order.created_at}</p>
    `;
    showPopup(detailedInfo);
}

function showPopup(detailedInfo) {
    const popup = document.getElementById('popup');
    const popupContent = document.getElementById('popup-content');
    
    if (!popup || !popupContent) {
        console.error('Popup elements not found in the DOM');
        return;
    }

    popupContent.innerHTML = detailedInfo;
    popup.style.display = 'flex';
}


document.addEventListener('DOMContentLoaded', function () {
    const popup = document.getElementById('popup');

    if (popup) {
        popup.addEventListener('click', function (e) {
            if (e.target === this) {
                closePopup();
            }
        });
    }
});

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}