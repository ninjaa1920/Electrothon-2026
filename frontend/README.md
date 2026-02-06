# Women Safety Analytics - Frontend

React-based web application with two distinct user flows.

## User Flows

### 1. Landing Page (`/`)
- User selects **Women** or **Police**.

### 2. Women Flow (`/women/*`)
- **Login/Register**: Captures Name, Email, Location Consent.
- **Dashboard**:
    - **Map View**: Shows current location & risk zones (Red/Yellow/Green).
    - **SOS Button**: Floating emergency action button.
    - **Notifications**: "⚠️ High-risk area detected".
    - *Note*: NO CCTV feeds here.

### 3. Police Flow (`/police/*`)
- **Verification**: Login with Name & Batch Number.
- **Dashboard**:
    - **CCTV Grid**: Live view of all connected cameras.
    - **AI Alerts Panel**: Incoming risk list.
- **High-Risk View**:
    - Auto-focuses on camera when Risk > High.
    - Shows Victim Name & Location.

## Setup & Run
```bash
npm install
npm run dev
```
