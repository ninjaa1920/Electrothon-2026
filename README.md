# Women Safety Analytics System

A comprehensive safety platform combining real-time AI video analytics with a role-based web application for Women and Police.

## Project Structure

- **`ai-engine/`**: Python-based computer vision system.
- **`backend/`**: Node.js/Express server/database.
- **`frontend/`**: React user interface.

## User Flows

### 🏠 Landing Page
Select your role: **Women** or **Police**.

### 👩 Women
1.  **Login/Register**: Provide Name, Email, Password, and Location Access.
2.  **Dashboard**:
    - **Map View**: See current location and nearby safe/risk zones.
    - **SOS**: Immediate emergency trigger.
    - **Alerts**: Receive notifications about high-risk areas.

### 🚓 Police
1.  **Verification**: Login with Police Name and Batch Number.
2.  **Dashboard**:
    - **CCTV Grid**: Monitor live camera feeds.
    - **AI Risk Panel**: Real-time list of automated risk alerts.
    - **High-Risk View**: When a critical event occurs (SOS or High Risk), the system focuses on the relevant feed and reveals the subject's identity/location.

## AI Engine Capabilities
- **Person & Gender Detection**: Identifies potential lone woman scenarios.
- **Proximity Analysis**: Detects "surrounded" or harassment situations.
- **SOS Recognition**: Detects hand gestures (e.g., Open Palm) for help.

## Getting Started

See the specific README files in each folder for detailed setup instructions:
- [AI Engine Instructions](./ai-engine/README.md)
- [Backend Instructions](./backend/README.md)
- [Frontend Instructions](./frontend/README.md)
