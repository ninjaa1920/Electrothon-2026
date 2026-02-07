document.addEventListener("DOMContentLoaded", () => {

  const socket = io();

  socket.on("connect", () => {
    console.log("✅ Connected to backend via Socket.IO");
  });

  let locationEnabled = false;
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
    locationEnabled = true;
    statusText.innerText = "Requesting location...";
    mapSection.style.display = "block";

    if (!mapInitialized) {
      map = L.map("map").setView([20.5937, 78.9629], 5);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);
      marker = L.marker([20.5937, 78.9629]).addTo(map);
      mapInitialized = true;
    }

    watchId = navigator.geolocation.watchPosition((pos) => {
      marker.setLatLng([pos.coords.latitude, pos.coords.longitude]);
      map.setView([pos.coords.latitude, pos.coords.longitude], 16);
      statusText.innerText = "Live tracking active";
    });
  }

  function disableLocation() {
    locationEnabled = false;
    if (watchId) navigator.geolocation.clearWatch(watchId);
    mapSection.style.display = "none";
    mapSection.style.border = "none";
    statusText.innerText = "Live tracking disabled";
    statusText.style.color = "";
  }

  enableBtn.addEventListener("click", enableLocation);
  disableBtn.addEventListener("click", disableLocation);

  // 🔴🟡🟢 RISK LISTENER
  socket.on("risk_update", (risk) => {
    console.log("⚠️ Risk update received:", risk);

    if (!locationEnabled) return;

    if (risk.level === "Vulnerable" || risk.level === "Critical") {
      mapSection.style.border = "6px solid red";
      statusText.innerText = "HIGH RISK";
      statusText.style.color = "red";
    } 
    else if (risk.level === "Moderate") {
      mapSection.style.border = "6px solid orange";
      statusText.innerText = "CAUTION";
      statusText.style.color = "orange";
    } 
    else {
      mapSection.style.border = "6px solid green";
      statusText.innerText = "SAFE";
      statusText.style.color = "green";
    }
  });

});