# ADR 0002: Tap Detection Method

## Status
Approved

## Context
AirType requires a reliable, low-latency gesture to trigger a "keystroke" (a "tap") over virtual key coordinates in mid-air. Standard webcams provide 2D image frames at 30 FPS. We must select a gesture heuristic that is easy for the user to perform, does not cause physical fatigue, has high precision (low false-positive rate), and has low latency.

We evaluated three potential techniques:
1. **Dwell-based (Hover-to-Select)**: The user hovers their fingertip over a key for a minimum duration (e.g., 400-600ms) to trigger a tap.
2. **Pinch-based (Index-to-Thumb Pinch)**: The user taps their index finger and thumb together to register a keystroke at the coordinates of the index fingertip.
3. **Depth/Z-axis Velocity-based**: The user moves their index finger forward toward the camera, and the ML pipeline detects a sharp acceleration in the Z-axis (relative depth) followed by a reversal to register a "tap".

### Trade-offs Evaluation
- **Dwell-based**:
  - *Pros*: Extremely simple to implement; no complex coordinate relationships; low false-positive rate.
  - *Cons*: Typing speed is severely capped (max ~15-20 WPM due to the forced dwell delays); feels sluggish and unnatural.
- **Pinch-based**:
  - *Pros*: Provides instant feedback; mimics physical pinching / tapping; can support higher typing speeds (30+ WPM); robust coordinate stability since the thumb acts as an anchor.
  - *Cons*: MediaPipe tracking may occasionally lose landmark precision during the occlusion of the thumb and index finger.
- **Depth/Z-axis Velocity-based**:
  - *Pros*: Fits the natural "typing in the air" paradigm.
  - *Cons*: Highly sensitive to camera angles, lighting, and lack of stereoscopic depth from monocular webcams; extremely high false-positive rate during hand movement; causes rapid hand fatigue.

## Decision
We choose **Pinch-based Tap Detection** as the primary default typing gesture. 

To mitigate tracking occlusion and maintain coordinate stability, the coordinate of the key targeted will be registered at the exact *moment of initial pinch contact*, using the coordinate of the index fingertip just *prior* to contact (to avoid coordinate drift when the fingers merge). 

We will also leave hooks in the `ml-service` to allow switching to alternative classifiers (e.g., a depth-based classifier) for research and benchmarking purposes.

## Consequences
- The ML state machine must track both the coordinates of the hand landmarks and the distance between the thumb tip and index tip.
- Datasets must include labeled examples of both "pinch" and "no-pinch" hand configurations under varying camera angles.
- High physical typing responsiveness, but requires robust filtering to prevent accidental pinches (false positives) when the hand is resting.
