# AirType Client

This is the React frontend for the **AirType** virtual keyboard system. It accesses the user's webcam, renders the keyboard interface, handles layout overlays, and visualizes the hand tracking landmarks in real time.

---

## Folder Contents
- `src/`: React source code (components, hooks, state, etc.).
- `public/`: Static files (index.html, logos, config overrides).
- `tests/`: Frontend component, utility, and integration tests.

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
To launch the React client application on port 3000:
```bash
npm start
```

### Running Tests
To run unit and component tests:
```bash
npm test
```

---

## Coding Guidelines
- Write all React components in TypeScript (`.tsx`).
- Keep components focused and modular (e.g., separate the webcam parser from the keyboard renderer).
- Do not make direct HTTP requests to the ML microservice. All communication must route through the `server` gateway layer.
- Run `npm run lint` and `npm run format` prior to committing.
