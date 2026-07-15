# Learning Journal: Lesson 8 - Tap Detection with Finite State Machine

## Date: 2026-07-15

Today we implemented depth-based tap detection. We designed a Finite State Machine (FSM) using hysteresis thresholds to provide software debouncing, enabling the system to emit clean keypress events in real-time.

---

## 1. What is Gesture Recognition?
In computer vision, **gesture recognition** is the process of translating human body movements (poses, paths, velocities, or configurations) into logical command events. 
For AirType, gesture recognition bridges the gap between raw spatial joint coordinates and system text inputs.

---

## 2. Why Hovering is Different from Pressing
A basic 2D pointer maps coordinates directly to actions (e.g. mouse movement). However, text typing requires a separate dimension to execute selection events:
- **Hovering (Targeting)**: Moving the pointer inside 2D space \((X, Y)\) to position the cursor over a key hitbox.
- **Pressing (Triggering)**: Performing a movement along the 3D depth axis \((Z)\) to choose and register the key.

Separating these operations prevents users from accidentally triggering every letter they slide their cursor across (called "slide-typing errors" or the "Midas touch problem").

---

## 3. Z-Axis Interpretation in MediaPipe
MediaPipe Hands outputs relative coordinates.
- The wrist landmark (`0`) is the reference origin \((0, 0, 0)\).
- **Z-coordinate**: Represents depth relative to the wrist.
- As the fingertip moves **closer to the camera** (forward push action), its Z-value becomes **more negative** (i.e. decreases relative to the wrist coordinate plane).
- As the fingertip moves **further from the camera** (retract action), its Z-value increases, moving back toward `0.0`.

---

## 4. Threshold Selection & Hysteresis
Using a single threshold depth value (e.g., $Z = -0.05$) to trigger clicks causes rapid, erratic clicking ("chatter") when a user rests their finger right at that depth.

To eliminate this noise, we apply **hysteresis (dual-threshold debouncing)**:
- **`press_threshold` (e.g., -0.06)**: The finger must push deep enough (Z value falls below `-0.06`) to transition to `PRESSED`.
- **`release_threshold` (e.g., -0.03)**: The finger must pull back far enough (Z value rises above `-0.03`) to transition back to `IDLE`.

This gap prevents coordinate micro-oscillations from triggering duplicate keystrokes.

---

## 5. Software Debouncing
In hardware keyboards, debouncing is a circuit process that filters out microscopic metal contact bounces when a key is struck. In AirType, **software debouncing** prevents coordinate noise from registering as multiple taps. By requiring the user to cross the release threshold before allowing another click, we debounce the input temporally.

---

## 6. Finite State Machines (FSM)
A **Finite State Machine (FSM)** is a mathematical model of computation. It consists of:
- A finite list of states (e.g. `IDLE` and `PRESSED`).
- An initial state (`IDLE`).
- Trigger conditions that govern state transitions.

```
       ┌──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  │ Z >= release_threshold
 ┌───────────┐      Z <= press_threshold (Event!)   ┌─────┴─────┐
 │   IDLE    ├─────────────────────────────────────►│  PRESSED  │
 └───────────┘                                      └───────────┘
```

### Why FSM is Used for Tap Detection
An FSM is ideal because:
1. **Edge Triggering**: It allows us to fire a keystroke event **only** on the transition path (`IDLE -> PRESSED`).
2. **Hold Locking**: While the state remains `PRESSED`, subsequent frames with deep Z-values do not trigger extra events. The user must lift their finger (transition back to `IDLE`) to type again.

---

## 7. How This Prepares the System for Text Input
Now that we can generate clean, debounced trigger events, the next lesson will introduce the **Typing Engine**. The typing engine will maintain a text buffer, append characters, handle backspace deletes, spacebar inputs, and render the output string on screen.
