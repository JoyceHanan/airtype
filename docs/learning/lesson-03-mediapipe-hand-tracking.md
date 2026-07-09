# Learning Journal: Lesson 3 - MediaPipe Hand Tracking

## Date: 2026-07-09

Today we integrated Google's **MediaPipe Hands** pipeline to track 21 three-dimensional coordinates of a human hand in real time. We abstracted MediaPipe's internals into a custom class and decoupled visualization overlays.

---

## 1. Why Hand Detection is Challenging
Detecting and tracking hands is one of the hardest problems in Computer Vision due to:
- **High Degrees of Freedom (DoF)**: The human hand has over 20 degrees of freedom, enabling a near-infinite variety of poses, flexes, and orientations.
- **Self-Occlusion**: Fingers frequently block each other relative to a single monocular webcam sensor (e.g., when making a fist or pinching).
- **Scale and Rotation**: Hands can be extremely close to the lens, far away, or tilted at various angles.
- **Background Clutter & Lighting**: The model must isolate the hand skin from background environments of similar coloration or under complex shadows.

---

## 2. Classical Computer Vision vs. Deep Learning
- **Classical CV (Heuristics)**:
  - *Methods*: Skin color segmentation (HSV filtering), contour matching, edge detection, and Haar Cascades.
  - *Limitations*: Highly fragile. A simple shift in lighting, wearing long sleeves, or showing a textured background breaks classical segmentation. It cannot resolve occluded finger joints.
- **Deep Learning**:
  - *Methods*: Convolutional Neural Networks (CNNs) trained on massive labeled datasets.
  - *Benefits*: Robust to illumination changes, backgrounds, and varying hand sizes. It generalizes feature representations (e.g., detecting a knuckle even if half-hidden).

---

## 3. Why MediaPipe Hands Was Chosen
MediaPipe Hands provides:
1. **CPU Real-Time Performance**: Runs at 30+ FPS on standard laptops without requiring a dedicated GPU.
2. **True 3D Coordinates**: Outputs 21 landmarks containing \(X, Y\) pixel coordinates and a relative \(Z\) depth coordinate.
3. **Optimized Multi-Stage Graph**: Employs a lightweight, hardware-accelerated pipeline model.

---

## 4. MediaPipe's Two-Stage Pipeline
To achieve fast performance, MediaPipe doesn't run the heavy landmark detector on every video frame. Instead, it uses a two-stage process:

```
                  ┌──────────────────────┐
                  │   Input Video Frame  │
                  └──────────┬───────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │    Palm Detection Model   │  ◄─── (Runs only on initial frame
               │  (Finds Hand Bounding Box)│        or if tracking is lost)
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │    Landmark Model (CNN)   │  ◄─── (Runs on cropped bounding box;
               │ (Predicts 21 3D Joint Pts)│        tracks landmarks frame-to-frame)
               └─────────────┬─────────────┘
                             │
               ┌─────────────┴─────────────┐
        Is hand still tracked successfully in crop?
               ├───► YES: Skip Palm Detection, reuse crop location next frame.
               └───► NO:  Trigger Palm Detection again.
```

- **Palm Detection (BlazePalm)**: First detects hand locations (bounding box). Palms are easier to locate than fingers because the palm is a rigid object with lower variance.
- **Hand Landmark Model**: Crop the bounding box containing the palm and pass it to a specialized regression model that predicts 21 landmark locations.

---

## 5. The 21 Landmarks
The MediaPipe Hands model outputs 21 landmarks mapped as follows:

```
          8 (Index Tip)  12 (Middle Tip)  16 (Ring Tip)  20 (Pinky Tip)
          |              |                |              |
          7 (Index DIP)  11 (Middle DIP)  15 (Ring DIP)  19 (Pinky DIP)
          |              |                |              |
    4     6 (Index PIP)  10 (Middle PIP)  14 (Ring PIP)  18 (Pinky PIP)
    |     \              |                |              /
    3      5 (Index MCP)─9 (Middle MCP)──13 (Ring MCP)──17 (Pinky MCP)
     \                                                 /
      2                                               /
       \                                             /
        1 (Thumb MCP)                               /
         \                                         /
          \                                       /
           └────────────── 0 (Wrist) ────────────┘
```

- **MCP**: Metacarpophalangeal Joint (Knuckles)
- **PIP**: Proximal Interphalangeal Joint (Middle joints)
- **DIP**: Distal Interphalangeal Joint (Top joints)

---

## 6. Normalized Coordinates
The \(X\) and \(Y\) coordinates returned by MediaPipe are **normalized between `0.0` and `1.0`** relative to the width and height of the image frame:
- `(0.0, 0.0)` is the **top-left corner**.
- `(1.0, 1.0)` is the **bottom-right corner**.

To convert them to physical pixels, we multiply by the frame dimensions:
\[x_{\text{pixel}} = x_{\text{normalized}} \times \text{Width}\]
\[y_{\text{pixel}} = y_{\text{normalized}} \times \text{Height}\]

The **\(Z\) coordinate** is different: it represents landmark depth relative to the wrist. The smaller the value, the closer the landmark is to the camera. It uses a scale roughly matching the \(X\) coordinates under orthographic projection.

---

## 7. Detection Confidence
- **`min_detection_confidence`**: Threshold (0.0 to 1.0) above which the initial palm detector must rank a region for it to be treated as a hand.
- **`min_tracking_confidence`**: Threshold above which the landmark model must rank coordinates for them to be considered valid in subsequent frames. If tracking falls below this value, the pipeline re-runs palm detection.

Setting these to `0.7` prevents random background textures (e.g., curtains, chairs) from triggering false hand tracks.

---

## 8. How AirType Will Use These Landmarks Later
1. **Cursor Targeting**: We will map the index fingertip landmark (`LANDMARK 8`) to coordinate bounds representing an on-screen virtual keyboard overlay.
2. **Pinch Activation**: To register a keystroke, we will calculate the Euclidean distance between the thumb tip (`LANDMARK 4`) and the index tip (`LANDMARK 8`). If the distance drops below a certain normalized threshold, a "tap" event is triggered.
3. **Coordinate Smoothing**: We will apply Double Exponential Smoothing to the coordinates of `LANDMARK 8` to eliminate high-frequency hand jitter, keeping the virtual cursor steady.
