document.addEventListener("DOMContentLoaded", () => {
  const socket = io();

  // UI Elements
  const locationStatus = document.getElementById("locationStatus");
  const riskLevelText = document.getElementById("riskLevelText");
  const sosBtn = document.getElementById("sosBtn");

  // Map Setup
  const map = L.map("map").setView([28.6139, 77.2090], 13); // Default New Delhi
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  let cameraMarker = null;

  socket.on("connect", () => {
    console.log("✅ Connected to backend");
    locationStatus.innerText = "System Online";
    locationStatus.className = "status success";
  });

  socket.on("disconnect", () => {
    locationStatus.innerText = "Disconnected";
    locationStatus.className = "status high";
  });

  // Handle Risk Updates (Continuous from AI)
  socket.on("risk_update", (data) => {
    console.log("Risk Update:", data);

    // Update Risk UI
    updateRiskUI(data.level);

    // Update Map with AI Location (Camera)
    if (data.latitude && data.longitude) {
      const lat = parseFloat(data.latitude);
      const lng = parseFloat(data.longitude);

      if (cameraMarker) {
        cameraMarker.setLatLng([lat, lng]);
      } else {
        cameraMarker = L.marker([lat, lng]).addTo(map)
          .bindPopup("<b>My Camera</b><br>Live Feed Location").openPopup();
        map.setView([lat, lng], 15);
      }
    }
  });

  function updateRiskUI(level) {
    riskLevelText.innerText = level.toUpperCase();

    // Reset classes
    riskLevelText.className = "status";

    if (level === "Safe") {
      riskLevelText.classList.add("low"); // Green
      riskLevelText.innerText = "SAFE";
      document.body.style.background = "linear-gradient(135deg, #d4edda, #c3e6cb)";
    } else if (level === "Moderate" || level === "Vulnerable") {
      riskLevelText.classList.add("high"); // Reuse high for orange/red or custom
      riskLevelText.style.background = "#fff3cd";
      riskLevelText.style.color = "#856404";
      document.body.style.background = "linear-gradient(135deg, #fff3cd, #ffeeba)";
    } else { // Critical
      riskLevelText.classList.add("high");
      document.body.style.background = "linear-gradient(135deg, #f8d7da, #f5c6cb)";
    }
  }

  // SOS Button Logic
  sosBtn.addEventListener("click", () => {
    // Find geolocation to send SOS (User's actual location if possible)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        socket.emit("new_alert", {
          riskLevel: "Critical",
          description: "MANUAL SOS TRIGGERED",
          location: "User_Mobile",
          latitude: latitude,
          longitude: longitude,
          timestamp: Date.now() / 1000
        });
        alert("SOS SENT with Location!");
      }, () => {
        // Fallback if geo fails
        socket.emit("new_alert", {
          riskLevel: "Critical",
          description: "MANUAL SOS TRIGGERED (No Loc)",
          location: "User_Mobile",
          timestamp: Date.now() / 1000
        });
        alert("SOS SENT!");
      });
    }
  });

});