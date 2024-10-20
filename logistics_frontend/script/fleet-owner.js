const API_BASE_URL = 'http://149.102.149.102:8000/api/v1';

document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('fleetOwnerToken');
    if (!token) {
        window.location.href = 'index.html';
    } else {
        document.body.style.display = 'block';
        console.log('User is authenticated');
    }
});
const jwtToken = `Bearer ${localStorage.getItem('fleetOwnerToken')}`;

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

// Password toggle
const passwordToggle = document.getElementById('passwordToggle');
const passwordInput = document.getElementById('password');

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

passwordToggle.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    passwordToggle.textContent = type === 'password' ? '👁️' : '🔒';
});

function updateDarkModeToggle(isDark) {
    darkModeToggle.textContent = isDark ? '☀️' : '🌓';
}

// Tab functionality
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabId = tab.getAttribute('data-tab');
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(`${tabId}Tab`).classList.add('active');
    });
});

// Toast functionality
function showToast(message, type) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.opacity = 1;
    setTimeout(() => {
        toast.style.opacity = 0;
    }, 3000);
}

// Fetch vehicle types and populate the select dropdown
async function fetchVehicleTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}/vehicle_type/get_names/`, {
            headers: {
                'Authorization': jwtToken,  // Ensure the JWT token is available
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        const vehicleTypeSelect = document.getElementById('vehicleType');

        if (data.success && data.data.vehicle_type_names) {
            vehicleTypeSelect.innerHTML = '<option value="">Select vehicle type</option>'; // Reset the options
            data.data.vehicle_type_names.forEach((type, index) => {
                const option = document.createElement('option');
                option.value = index + 1; 
                option.textContent = type;
                vehicleTypeSelect.appendChild(option);
            });
        } else {
            showToast('Failed to load vehicle types', 'error');
        }
    } catch (error) {
        showToast('Error fetching vehicle types', 'error');
    }
}

// Call fetchVehicleTypes when the page loads
fetchVehicleTypes();


// Fetch drivers
async function fetchDrivers() {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/view_drivers/`, {
            headers: {
                'Authorization': jwtToken
            }
        });
        const data = await response.json();
        const driverTable = document.getElementById('driverTable').getElementsByTagName('tbody')[0];
        driverTable.innerHTML = '';
        data.data.drivers.forEach(driver => {
            const row = driverTable.insertRow();
            


            row.innerHTML = `
                <td>${driver.name}</td>
                <td>${driver.phone}</td>
                <td>${driver.license_number}</td>
                <td>${driver.location ? `<a href="${driver.location}" target="_blank">Link</a>` : 'None'}</td>
                <td>${driver.status}</td>
                <td>${driver.availability_status ? '✅' : '❌'}</td>
            `;
        });
        updateAssignDriverSelect(data.data.drivers);
    } catch (error) {
        showToast('Failed to fetch drivers', 'error');
    }
}

// Fetch vehicles
async function fetchVehicles() {
    try {
        const response = await fetch('/api/v1/fleet_owner/view_vehicles/', {
            headers: {
                'Authorization': jwtToken
            }
        });
        const data = await response.json();
        const vehicleTable = document.getElementById('vehicleTable').getElementsByTagName('tbody')[0];
        vehicleTable.innerHTML = '';
        data.data.vehicles.forEach(vehicle => {
            const row = vehicleTable.insertRow();
            row.innerHTML = `
                <td>${vehicle.license_plate}</td>
                <td>${vehicle.vehicle_type}</td>
                <td>${vehicle.capacity}</td>
                <td>${vehicle.make}</td>
                <td>${vehicle.model}</td>
                <td>${vehicle.year}</td>
                <td>${vehicle.color}</td>
                <td>${vehicle.driver || 'Unassigned'}</td>
                <td>${vehicle.driver ? `<button onclick="deassignVehicle(${vehicle.vehicle_id})">Deassign</button>` : ''}</td>
            `;
        });
        updateAssignVehicleSelect(data.data.vehicles);
        updateDeassignVehicleSelect(data.data.vehicles);
    } catch (error) {
        showToast('Failed to fetch vehicles', 'error');
    }
}

// Add driver
document.getElementById('addDriverForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const driverData = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/add_driver/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': jwtToken
            },
            body: JSON.stringify(driverData),
        });
        if (response.ok) {
            showToast('Driver added successfully', 'success');
            e.target.reset();
            fetchDrivers();
        } else {
            throw new Error('Failed to add driver');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Add vehicle
document.getElementById('addVehicleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const vehicleData = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/add_vehicle/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': jwtToken
            },
            body: JSON.stringify(vehicleData),
        });
        if (response.ok) {
            showToast('Vehicle added successfully', 'success');
            e.target.reset();
            fetchVehicles();
        } else {
            throw new Error('Failed to add vehicle');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Assign vehicle
document.getElementById('assignVehicleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const assignData = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/assign_vehicle/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': jwtToken
            },
            body: JSON.stringify(assignData),
        });
        if (response.ok) {
            showToast('Vehicle assigned successfully', 'success');
            e.target.reset();
            fetchVehicles();
        } else {
            throw new Error('Failed to assign vehicle');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Deassign vehicle
document.getElementById('deassignVehicleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const deassignData = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/deassign_vehicle/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': jwtToken
            },
            body: JSON.stringify(deassignData),
        });
        if (response.ok) {
            showToast('Vehicle deassigned successfully', 'success');
            e.target.reset();
            fetchVehicles();
        } else {
            throw new Error('Failed to deassign vehicle');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Fetch vehicles by driver
async function fetchVehiclesByDriver() {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet_owner/view_vehicles_by_driver/`, {
            headers: {
                'Authorization': jwtToken
            }
        });
        const data = await response.json();
        const vehiclesByDriverTable = document.getElementById('vehiclesByDriverTable').getElementsByTagName('tbody')[0];
        vehiclesByDriverTable.innerHTML = '';
        data.data.vehicles.forEach(vehicle => {
            const row = vehiclesByDriverTable.insertRow();
            row.innerHTML = `
                <td>${vehicle.vehicle_id}</td>
                <td>${vehicle.license_plate}</td>
                <td>${vehicle.vehicle_type}</td>
                <td>${vehicle.driver_id}</td>
                <td>${vehicle.driver_name}</td>
                <td>${vehicle.driver_phone}</td>
                <td>${vehicle.status}</td>
                <td>${vehicle.availability_status ? '✅' : '❌'}</td>
            `;
        });
    } catch (error) {
        showToast('Failed to fetch vehicles by driver', 'error');
    }
}

// Update assign driver select
function updateAssignDriverSelect(drivers) {
    const select = document.getElementById('assignDriver');
    select.innerHTML = '<option value="">Select driver</option>';
    drivers.forEach(driver => {
        const option = document.createElement('option');
        option.value = driver.driver_id;
        option.textContent = `${driver.name}`;
        select.appendChild(option);
    });
}

// Update assign vehicle select
function updateAssignVehicleSelect(vehicles) {
    const select = document.getElementById('assignVehicle');
    select.innerHTML = '<option value="">Select vehicle</option>';
    vehicles.filter(v => !v.driver).forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.vehicle_id;
        option.textContent = `${vehicle.license_plate} - ${vehicle.make} ${vehicle.model}`;
        select.appendChild(option);
    });
}

// Update deassign vehicle select
function updateDeassignVehicleSelect(vehicles) {
    const select = document.getElementById('deassignVehicle');
    select.innerHTML = '<option value="">Select vehicle</option>';
    vehicles.filter(v => v.driver).forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.vehicle_id;
        option.textContent = `${vehicle.license_plate} - ${vehicle.make} ${vehicle.model} (Driver: ${vehicle.driver})`;
        select.appendChild(option);
    });
}

// Refresh buttons
document.getElementById('refreshDrivers').addEventListener('click', fetchDrivers);
document.getElementById('refreshVehicles').addEventListener('click', fetchVehicles);
document.getElementById('refreshVehiclesByDriver').addEventListener('click', fetchVehiclesByDriver);

// Initial data fetch
fetchDrivers();
fetchVehicles();
fetchVehiclesByDriver();

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
    localStorage.removeItem('token');

    window.location.href = 'index.html';
});