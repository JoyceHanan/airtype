# AirType ML Service

This is the Python microservice responsible for real-time 3D hand landmark tracking, gesture modeling, tap-vs-hover classification, and key coordination calculations.

---

## Folder Contents
- `src/`: Core Python pipeline scripts.
  - `src/pipeline/`: MediaPipe integration and landmark coordinate extraction.
  - `src/classifiers/`: Heuristic and model-based classifiers (pinch detection, depth thresholding).
  - `src/state_machine/`: Finite State Machine managing keyboard typing interactions (Hover, Active, Tap, Release).
- `tests/`: Unit and calculation tests.

---

## Development Setup

### Dependencies
Requires Python 3.10 or 3.11.

### Installation
From the root directory:
```bash
npm run setup
```
Or inside this directory, create and activate a virtual environment, then install requirements:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally
To launch the FastAPI server in development hot-reload mode on port 8000:
```bash
uvicorn src.main:app --reload --port 8000
```

### Running Tests
To run PyTest unit checks:
```bash
pytest
```

---

## Algorithm Specifications
- **Tracking Pipeline**: Built using Google MediaPipe Hands SDK.
- **Coordinate Filtering**: Utilizes Double Exponential Smoothing to reduce optical jitter in 3D landmarks.
- **Classification Method**: Pinch detection is implemented by thresholding the Euclidean distance between the index fingertip (`LANDMARK 8`) and thumb tip (`LANDMARK 4`), normalized by the user's hand scale parameter.
