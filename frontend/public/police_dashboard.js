const socket = io();

socket.on("connect", () => {
    console.log("✅ Police dashboard connected to backend");
});

/* ================= MAP SETUP ================= */
// Default View: India Center
let map = L.map("map").setView([20.5937, 78.9629], 5);
let alertCircle = null;
let alertMarker = null;

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

/* ================= UI ELEMENTS ================= */
const statusBar = document.getElementById("statusBar");
const statusText = document.getElementById("statusText");
const riskLevelText = document.getElementById("riskLevel");
const riskReasonText = document.getElementById("riskReason");
const locationIdText = document.getElementById("locationId");
const riskScoreText = document.getElementById("riskScore");

/* ================= SOCKET LISTENER ================= */
socket.on("risk_update", (risk) => {
    console.log("🚨 Risk update received:", risk);

    // 1. EXTRACT DATA
    // Use received Lat/Long if available, otherwise default to New Delhi
    const lat = risk.latitude || 28.6139;
    const lng = risk.longitude || 77.2090;
    const alertLatLng = [lat, lng];

    // Update Text Fields
    locationIdText.innerText = risk.location || "Unknown";
    riskScoreText.innerText = risk.riskScore ? `${risk.riskScore}%` : "--";

    // Remove old visual elements
    if (alertCircle) map.removeLayer(alertCircle);
    if (alertMarker) map.removeLayer(alertMarker);

    /* ===== SAFE ===== */
    if (risk.level === "Safe") {
        statusBar.className = "status-bar safe";
        statusText.innerText = "🟢 STATUS: SAFE";
        riskLevelText.innerText = "Safe";
        riskReasonText.innerText = "No threat detected";

        // Optional: Blue circle for active monitoring but safe
        alertCircle = L.circle(alertLatLng, {
            radius: 100,
            color: "blue",
            fillColor: "#2196f3",
            fillOpacity: 0.1,
        }).addTo(map);
    }

    /* ===== MODERATE ===== */
    else if (risk.level === "Moderate" || risk.level === "Vulnerable") {
        statusBar.className = "status-bar alert";
        statusText.innerText = "🟠 STATUS: MODERATE ALERT";
        riskLevelText.innerText = risk.level;
        riskReasonText.innerText = risk.description || "Suspicious activity";

        alertCircle = L.circle(alertLatLng, {
            radius: 300,
            color: "orange",
            fillColor: "#ff9800",
            fillOpacity: 0.4,
        }).addTo(map);

        alertMarker = L.marker(alertLatLng).addTo(map)
            .bindPopup(`<b>${risk.location}</b><br>${risk.description}`).openPopup();

        // Zoom to alert
        map.setView(alertLatLng, 16);
    }

    /* ===== CRITICAL / HIGH ===== */
    else {
        statusBar.className = "status-bar critical"; // Different class for red
        statusText.innerText = "🔴 STATUS: CRITICAL ALERT";
        riskLevelText.innerText = risk.level;
        riskReasonText.innerText = risk.description || "Severe threat detected";

        alertCircle = L.circle(alertLatLng, {
            radius: 500,
            color: "red",
            fillColor: "#f44336",
            fillOpacity: 0.5,
        }).addTo(map);

        alertMarker = L.marker(alertLatLng).addTo(map)
            .bindPopup(`<b>${risk.location}</b><br>CRITICAL: ${risk.description}`).openPopup();

        // Zoom and Fly
        map.flyTo(alertLatLng, 17);
    }
});
