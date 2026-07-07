# ADR 0004: Gateway Layer vs. Direct Python Backend

## Status
Approved

## Context
AirType has two primary domains of operations:
1. **Core Web Services**: Authentication, user session management, keyboard layout definitions, typing history, and API routes.
2. **ML Pipeline Execution**: Real-time video frame ingest, 3D hand tracking, gesture classification, and state machine updates.

We must decide whether to route client requests directly to a single Python-based web server (e.g., FastAPI, Django, Flask) that handles both domains, or use a Node.js/Express gateway that proxies heavy ML operations to a separate Python microservice.

### Options
1. **Single Python Backend**: All routing, auth, database actions, and MediaPipe tracking coordinate processing exist in a single Python application.
2. **Node.js Gateway + Python ML Microservice**: A Node.js Express server handles standard web operations, database connections, and auth, while a dedicated Python microservice executes the ML pipeline.

### Trade-offs Evaluation
- **Single Python Backend**:
  - *Pros*: Simpler architecture (one less service to run and configure); no network transit overhead between gateway and ML services.
  - *Cons*: Node.js has historically better package support and higher concurrency scaling for real-time WebSocket traffic (which we will use for coordinates streaming); database drivers and OAuth modules are highly mature in Node; combining web services and CPU-bound ML tracking in Python risks blocking the asyncio event loop under high load.
- **Node.js Gateway + Python ML Microservice**:
  - *Pros*: Clean separation of concerns. The Node.js gateway handles high-concurrency connections (WebSockets/HTTP), auth, and user history without blockages. The ML service is dedicated to mathematical modeling and computer vision. ML models can be scaled or updated independently.
  - *Cons*: Additional microservice configuration; slight network latency penalty (~1-3ms) when proxying coordinate streams.

## Decision
We choose to use a **Node.js/Express Gateway** in front of a **Python ML Microservice**.

The client app communicates directly with the Node.js Gateway. For coordinate streams, the Gateway proxies the data to the Python microservice using low-latency WebSockets or gRPC. This allows us to keep the web application simple and highly concurrent, while preserving Python's extensive ecosystem for machine learning and data science without polluting the web gateway.

## Consequences
- The developer must run both the Node.js server and Python service in the local development environment (orchestrated via `scripts/run_dev.sh`).
- High modularity: We can replace the frontend client or Node server without touching any computer vision or tap-detection code.
- Clear contract between services: Coordinates and predicted taps are passed through defined WebSocket / JSON payloads.
