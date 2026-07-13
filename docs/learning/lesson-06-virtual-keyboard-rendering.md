# Learning Journal: Lesson 6 - Virtual Keyboard Rendering

## Date: 2026-07-13

We implemented a modular virtual keyboard model and rendering overlay. By separating the keyboard configurations from raw canvas operations and establishing correct draw ordering, we created a scalable interface layout.

---

## 1. Why Model a Key as an Object
A key in a virtual typing layout is a physical active region on the screen coordinate space.
Modeling it as a structured object:
- **Bundles Coordinates and Identity**: Grouping coordinate bounds (`x, y, width, height`) alongside key values (`label`) ensures that collision checkers can inspect boundaries quickly.
- **Enables State Tracking**: In future lessons, keys will need state properties to trace interactive behavior (e.g. `is_hovered`, `is_pressed`, `hover_duration`). Encapsulating these inside the object data container prevents cluttering the tracking code.

---

## 2. Separation of Data and Rendering
Conforming to clean architecture standards:
- **`Key` (Data Model)**: Pure coordinate parameters. No dependencies on rendering packages (`cv2`).
- **`KeyboardLayout` (Layout Generator)**: Computes matrix proportions. Tells the app where keys should live based on frame boundaries. No visual design logic.
- **`KeyboardRenderer` (Drawing engine)**: Handles pixels, border thickness, text alignments, and alpha transparencies. No layout geometry logic.

This decoupling means that modifying visual themes (fonts, transparency settings) is isolated to the renderer, while shifting key configurations (e.g. Dvorak layouts) is isolated to the layout configuration module.

---

## 3. Keyboard Layout Generation
For AirType, we partitioned the camera feed canvas:
- **Interaction Screen Division**: The keyboard sits on the lower 40% of the screen area (\(Y_{\text{start}} = 55\%\)), leaving the top half open for camera hand landmarks visual tracking.
- **Centered Columns Alignment**: Row 1 has 10 keys (base width division). Row 2 contains 9 keys, which we offset horizontally by half key width to center the row. Row 3 contains 7 characters and a double-wide Backspace key. Row 4 features a centered spacebar mapped to 6 standard key widths.

This dynamic grid scaling uses relative dimension offsets so the virtual keyboard scales automatically if camera feed resolutions change.

---

## 4. The Rendering Pipeline
To draw the virtual keyboard without obscuring the background feed or the hand overlay:

```
[Raw Camera Frame]
       │
       ▼ (Pass to KeyboardRenderer)
[Draw Filled Transparent Rectangles (cv2.rectangle)]
       │
       ▼ (Blend Fill using cv2.addWeighted)
[Alpha-Blended Translucent Frame]
       │
       ▼ (Draw Opaque Key Borders & Centered Labels)
[Sharp Keyboard Overlay Frame]
       │
       ▼ (Pass to LandmarkDrawer)
[Overlay Hand Landmarks & Tracker Pointers] (Drawn on top)
       │
       ▼
[Final Screen Display]
```

### Centering Labels
To center text labels inside keys dynamically, we query the text bounding box metrics:
\[x_{\text{text}} = x_{\text{key}} + \frac{W_{\text{key}} - W_{\text{text}}}{2}\]
\[y_{\text{text}} = y_{\text{key}} + \frac{H_{\text{key}} + H_{\text{text}}}{2}\]

---

## 5. Why this Architecture is Scalable
- **Swappable Layout engines**: We can support multiple input layout mappings (e.g., numerical keypads, emoji panels) by substituting the layout generator class with a class implementing a common interface.
- **Platform Portability**: Because the key coordinate math is clean and platform-independent, we can package this coordinate table in JSON format and stream it directly to a web frontend client (Vite/React) for rendering in a browser, rather than drawing natively with Python OpenCV.

---

## 6. How Future Interaction Modules Will Use the Keyboard
- **Hover Detection**: The coordinate checking pipeline will query `KeyboardLayout.get_keys()` and check if the smoothed fingertip coordinate falls inside key bounds:
  \[x_{\text{key}} \le x_{\text{fingertip}} < x_{\text{key}} + W_{\text{key}}\]
  \[y_{\text{key}} \le y_{\text{fingertip}} < y_{\text{key}} + H_{\text{key}}\]
- **Visual Feedback**: If the coordinate is within a key bounding box, the hover detection module will mark the key as hovered (`key.is_hovered = True`). The renderer will check this flag and draw it in a highlighted color (e.g., neon yellow border) to give visual feedback to the user.
