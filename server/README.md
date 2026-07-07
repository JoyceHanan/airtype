# AirType Gateway Server

This is the Node.js / Express backend for **AirType**. It acts as the API Gateway, handles auth and user sessions, records typing history, and proxies webcam streams to the Python ML microservice.

---

## Folder Contents
- `src/`: Express routes, middleware, and ML proxy handlers.
- `tests/`: API integration and unit tests.

---

## Development Setup

### Dependencies
Before running, ensure you have Node.js (v18.x or v20.x) installed.

### Installation
From the root directory:
```bash
npm run setup
```
Or inside this directory:
```bash
npm install
```

### Running Locally
To launch the gateway server in development mode (with nodemon hot-reloading) on port 5000:
```bash
npm run dev
```

### Running Tests
To run API integration tests:
```bash
npm test
```

---

## Technical Architecture & Routes
- `/api/auth`: User registration, login, and token generation.
- `/api/session`: CRUD operations for user typing sessions and character metrics.
- `/api/config`: Returns screen coordinates, keyboard physical layout constants, and client calibration parameters.
- `/ws/stream`: WebSocket endpoint. Proxies incoming coordinates from the client to the ML service, returning classification events (taps, hovers).
