# Learning Journal: Lesson 4 - Fingertip Tracking and Coordinate Mapping

## Date: 2026-07-10

We implemented coordinate mapping and index fingertip extraction. By decoupling the spatial math from the visualization overlays, we created a testable tracking pipeline.

---

## 1. MediaPipe Landmark Indexing
Google MediaPipe Hands returns a sequential array of 21 landmarks representing joint coordinates. These indices are fixed and standard:
- `0`: Wrist
- `1` to `4`: Thumb (from joint base to tip)
- `5` to `8`: Index Finger (from knuckle to tip)
- `9` to `12`: Middle Finger (from knuckle to tip)
- `13` to `16`: Ring Finger (from knuckle to tip)
- `17` to `20`: Pinky Finger (from knuckle to tip)

To track a virtual cursor, we specifically focus on **Landmark 8 (`INDEX_FINGER_TIP`)**, which represents the tip of the index finger.

---

## 2. Normalized Coordinates
MediaPipe coordinates are expressed as normalized floats:
- \(X_{\text{norm}}, Y_{\text{norm}}\) range from `0.0` (top-left) to `1.0` (bottom-right).
- Normalized coordinates are **resolution-independent**. They remain identical whether the camera records at `640x480` or `1920x1080`.
- The \(Z\) coordinate represents relative depth. It is calculated by estimating the distance from the wrist to the camera. The smaller the value, the closer the finger is to the camera lens.

---

## 3. Pixel Coordinates
To draw overlays on a window or map coordinates to an active GUI layout, normalized floats must be translated into **discrete pixel integers**:
\[x_{\text{pixel}} = \text{int}(x_{\text{norm}} \times \text{Frame Width})\]
\[y_{\text{pixel}} = \text{int}(y_{\text{norm}} \times \text{Frame Height})\]

### Spatial Boundary Guarding (Clipping)
Due to lens distortion or hand tracking projections, landmarks may occasionally return values slightly outside the range `[0.0, 1.0]` (e.g., `-0.02` or `1.03`). 
If we multiply these values by frame dimensions directly, we can get pixel coordinates outside array bounds (e.g., a pixel index of `-12` or `645` on a `640`-width matrix), causing array index out-of-bound crashes.
We enforce defensive clipping limits:
\[x_{\text{clipped}} = \max(0, \min(x_{\text{pixel}}, \text{Frame Width} - 1))\]
\[y_{\text{clipped}} = \max(0, \min(y_{\text{pixel}}, \text{Frame Height} - 1))\]

---

## 4. Coordinate Mapping
Coordinate mapping is the process of translating coordinates from one coordinate system to another.
In AirType, we map coordinate values across multiple spaces:

```
[Normalized Space] (0.0 to 1.0) 
       │
       ├─► Multiply by camera resolution ──► [Camera Pixel Space] (e.g., 640x480)
       │
       └─► Map to virtual layout grid ────► [Keyboard Screen Space] (e.g., target key coordinates)
```

---

## 5. Why Coordinate Systems Matter
Coordinate systems matter because different tasks require different spatial properties:
- **Tracking (Normalized)**: Keeps model inference scale-invariant and camera-independent.
- **Rendering (Camera Pixel)**: Required to display tracking overlays correctly on the video feed.
- **Typing (Keyboard Layout)**: Required to detect which virtual key boundaries (e.g., the bounding box of the letter 'A') contain the fingertip coordinate.

---

## 6. How AirType Will Use Fingertip Tracking
In subsequent lessons, fingertip coordinates will drive the virtual keyboard:
1. **Cursor Targeting**: The coordinates of `Landmark 8` will hover over virtual keys.
2. **Dynamic Calibration**: We will define calibration loops where the user touches corners of their screen to map their physical hand travel comfort zone to the coordinates of the typing layout.
3. **Double Exponential Smoothing**: Hand movements naturally contain minor muscular jitter. We will apply a low-pass filter to the coordinate stream to prevent the cursor from jumping erratically between adjacent letters.

---

## 7. Engineering Design Decisions for the Processing Layer

### Decoupled Data Contracts
We introduced a custom `FingertipData` dataclass. It contains both raw normalized floats and physical integers, as well as the relative depth:
```python
@dataclass(frozen=True)
class FingertipData:
    pixel_coords: Tuple[int, int]
    normalized_coords: Tuple[float, float]
    depth: float
```
- By making it `frozen=True` (immutable), we prevent downstream modules from accidentally mutating coordinate values.
- Downstream modules interact solely with `FingertipData`, completely decoupling them from the raw index array mapping of MediaPipe Hands.
