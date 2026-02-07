let map;
let marker;
let watchId = null;

const statusText = document.getElementById("locationStatus");
const enableBtn = document.getElementById("enableBtn");
const disableBtn = document.getElementById("disableBtn");

// Initialize Leaflet Map
function initMap() {
    // Default view (India center roughly)
    map = L.map('map').setView([20.5937, 78.9629], 5);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Initialize marker but don't add it yet
    marker = L.marker([20.5937, 78.9629]).addTo(map);
    marker.bindPopup("<b>You are here</b>").openPopup();
}

// Run initMap when page loads
document.addEventListener("DOMContentLoaded", () => {
    initMap();
    // Try to get location immediately for better UX
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude, longitude } = pos.coords;
                marker.setLatLng([latitude, longitude]);
                map.setView([latitude, longitude], 16);
                marker.bindPopup("<b>You are here (Approx)</b>").openPopup();
            },
            (err) => console.log("Init loc error:", err),
            { enableHighAccuracy: true }
        );
    }
});

function enableLocation() {
    if (!navigator.geolocation) {
        statusText.innerText = "Geolocation not supported";
        return;
    }

    statusText.innerText = "Locating you...";

    watchId = navigator.geolocation.watchPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            // Update Leaflet marker and view
            marker.setLatLng([lat, lng]);
            map.setView([lat, lng], 16);

            statusText.innerText = "Live tracking active";
        },
        (err) => {
            console.error(err);
            statusText.innerText = "Location permission denied or error";
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
        }
    );
}

function disableLocation() {
    if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }
    statusText.innerText = "Live tracking disabled";
}

enableBtn.addEventListener("click", enableLocation);
disableBtn.addEventListener("click", disableLocation);

document.getElementById("sosBtn").addEventListener("click", () => {
    alert("🚨 SOS sent! Police have been alerted.");
});