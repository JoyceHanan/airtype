# ADR 0003: MediaPipe Hands Tracking

## Status
Approved

## Context
AirType requires real-time, low-latency tracking of 21 3D hand landmarks (fingertips, knuckles, wrist) from raw video frames captured by a standard laptop webcam. This tracking must run locally on consumer-grade hardware (laptops without dedicated GPUs) without introducing noticeable input lag.

We evaluated the following options:
1. **OpenPose / Custom CNN**: Training a custom convolutional neural network or deploying OpenPose.
2. **Ultralytics YOLOv8-pose**: Deploying a posture/pose estimation model trained on hand datasets.
3. **Google MediaPipe Hands**: An off-the-shelf, highly optimized framework for real-time 3D hand tracking.

### Trade-offs Evaluation
- **OpenPose / Custom CNN**:
  - *Pros*: Custom architectures can be highly tailored to specific camera layouts.
  - *Cons*: Extremely resource-intensive; running OpenPose locally on CPU is slow (frequently < 10 FPS); requires massive labeled hand datasets to train a custom model from scratch.
- **YOLOv8-pose**:
  - *Pros*: State-of-the-art accuracy; robust to occlusion.
  - *Cons*: Substantial computation overhead; requires GPU for sub-30ms execution; lacks hand-specific optimized frameworks compared to MediaPipe.
- **MediaPipe Hands**:
  - *Pros*: Runs efficiently on average CPU platforms (supporting 30+ FPS on consumer laptops); outputs 21 3D hand landmarks; cross-platform support (Python, JS, Android, iOS); lightweight packages; active open-source support.
  - *Cons*: Accuracy drops slightly in low-light environments; Z-coordinates are relative (calculated from camera distance estimates rather than stereoscopic depth).

## Decision
We choose **Google MediaPipe Hands** for real-time landmark tracking. 

The relative Z-coordinates provided by MediaPipe will be processed using our own filtering heuristics (e.g., Double Exponential Smoothing) to filter jitter. If latency or CPU overhead becomes an issue on low-end systems, we will explore MediaPipe's lightweight model options (model complexity 0 vs. model complexity 1).

## Consequences
- No custom deep learning hardware or heavy GPUs are required to run the local developer environment.
- The pipeline will ingest MediaPipe output directly.
- The system depends on MediaPipe's licensing and Python bindings (`mediapipe` library). We will create a wrapper class around the tracking library to allow swapping it out if an alternative framework is chosen later.
