# Women Safety Analytics - Backend

Express.js server handling Authentication, Alerts, and Real-time communication.

## Responsibilities
1.  **Auth Management**:
    - **Women**: Register/Login, Store Location Consent (`/api/women/auth`).
    - **Police**: Verify Batch Numbers (`/api/police/auth`).
2.  **Alert Dispatch**:
    - Receives alerts from **AI Engine**.
    - Broadcasts high-risk alerts to **Police Dashboard** via Socket.io.
    - Sends notifications to **Women App** (e.g., "High Risk Zone detected").
3.  **Database**:
    - MongoDB stores User profiles, Police records, and Alert history.

## Setup & Run
```bash
npm install
npm start
```

## API Routes (Planned)
- `POST /api/women/register`
- `POST /api/police/verify`
- `POST /api/alert` (from AI)
- `GET /api/alerts` (for History)
