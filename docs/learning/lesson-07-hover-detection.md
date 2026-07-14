# Learning Journal: Lesson 7 - Hover Detection Using Bounding Box Collision

## Date: 2026-07-14

Today we implemented a real-time hover detection algorithm using Point-in-Rectangle collision checking. We created a separate collision module and integrated active key highlighting.

---

## 1. Point-in-Rectangle Collision Detection
Point-in-Rectangle collision checking (also known as an **Axis-Aligned Bounding Box (AABB)** collision check) verifies if a single 2D coordinate point \((P_x, P_y)\) resides inside the area defined by a rectangle.

A rectangle in pixel coordinate space is defined by its top-left corner \((X, Y)\), a width \(W\), and a height \(H\). The boundaries are:
- Horizontal range: \([X, X + W]\)
- Vertical range: \([Y, Y + H]\)

A collision occurs if and only if both conditions are satisfied:
\[X \le P_x < X + W\]
\[Y \le P_y < Y + H\]

In Python, this translates to:
```python
if (key.x <= finger_x < key.x + key.width) and (key.y <= finger_y < key.y + key.height):
    # Collision occurred!
```

---

## 2. Hitboxes
In game design and human-computer interaction, a **hitbox** is an invisible boundary shape used to detect collision events.
- **Physical Keys vs. Hitboxes**: While the visual representation of a key contains margins, rounded borders, and inner labels, the *hitbox* is the active coordinate check region.
- **Hitbox Padding**: Hitboxes do not have to map to visual bounds. For example, if users frequently overshoot key borders, we can expand key hitboxes internally (adding invisible padding) to make keys easier to hit. Separating the model data from the renderer enables this layout flexibility.

---

## 3. Why Collision Detection Belongs in Its Own Module
Placing collision checks inside key models or the tracking loop creates tight coupling:
- **Separation of Concerns**: Calculating spatial overlaps is an analytical geometric task. The tracker should only output coordinates, and the key model should only store values.
- **Multi-Layout Flexibility**: A standalone `HoverDetector` can check coordinates against *any* layout representation (e.g. circles on custom layouts, split keyboard models) without modifying the main tracking loops.
- **Unit Testability**: We can easily test collision logic by passing mock coordinates (e.g., coordinate `(100, 100)`) against mock keys, verifying return outputs without requiring webcam inputs or graphic rendering windows.

---

## 4. Why Interaction is Separated from Rendering
- **Visuals are Downstream**: The interaction module determines *what* happens (e.g., "Finger is over Key Q"). The renderer determines *how* to represent that state (e.g., "Draw Key Q with a cyan glow").
- **State Integrity**: The renderer reads state configurations but does not mutate them. This guarantees data consistency. If we decided to port AirType from OpenCV window rendering to a browser canvas, the collision math logic remains completely unchanged.

---

## 5. How Hover Detection Prepares the System for Tap Detection
Hover detection handles **Targeting** (which key is the user aiming at). Tap detection handles **Triggering** (when does the user make a selection).

```
                      ┌────────────────────────┐
                      │ Smoothed Fingertip Coords│
                      └───────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │      HoverDetector      │
                     │ (Finds Target Key 'K')  │
                     └────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │      Tap Classifier      │ ──► (Triggers tap gesture?)
                    └─────────────┬────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          ├───► YES: Output keystroke 'K' to text buffer.
          └───► NO:  Maintain cursor hover highlight state.
```

When the user performs a click gesture (like a pinch), the system queries the `HoverDetector` to identify the hovered key at that exact frame to output the letter, completing the typing action cleanly.
