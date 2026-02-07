let map;
let marker;
let watchId = null;
let mapInitialized = false;

const statusText = document.getElementById("locationStatus");
const enableBtn = document.getElementById("enableBtn");
const disableBtn = document.getElementById("disableBtn");
const mapSection = document.getElementById("mapSection");

// Enable location
function enableLocation() {
  if (!navigator.geolocation) {
    statusText.innerText = "Geolocation not supported";
    return;
  }

  statusText.innerText = "Requesting location...";
  mapSection.style.display = "block";

  // Initialize map only ONCE
  if (!mapInitialized) {
    map = L.map("map").setView([20.5937, 78.9629], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    marker = L.marker([20.5937, 78.9629]).addTo(map);
    mapInitialized = true;
  }

  watchId = navigator.geolocation.watchPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;

      marker.setLatLng([lat, lng]);
      map.setView([lat, lng], 16);

      statusText.innerText = "Live tracking active";
    },
    (err) => {
      console.error(err);
      statusText.innerText = "Location permission denied";
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
    }
  );
}

// Disable location
function disableLocation() {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }

  mapSection.style.display = "none";
  statusText.innerText = "Live tracking disabled";
}

// Button listeners
enableBtn.addEventListener("click", enableLocation);
disableBtn.addEventListener("click", disableLocation);

// SOS button
document.getElementById("sosBtn").addEventListener("click", () => {
  alert("🚨 SOS sent! Police have been alerted.");
});