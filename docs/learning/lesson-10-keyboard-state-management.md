# Learning Journal: Lesson 10 - Keyboard State Management

## Date: 2026-07-19

Today we introduced a dedicated **KeyboardController** to manage keyboard-specific state and mapping rules (such as Shift and Caps Lock states, key mapping translations). Conforming to Clean Architecture guidelines, we simplified the `TextBuffer` to be a pure data store and updated the virtual keyboard layout to expose Shift and Caps Lock keys on the grid.

---

## 1. Keyboard State
In input engineering, **keyboard state** refers to the dynamic configuration settings that modify what characters are output when standard keys are pressed:
- **Modifier Keys**: Keys that change other inputs rather than printing characters directly (e.g. Shift, Ctrl, Alt).
- **Toggle States**: Persistent lock settings (e.g. Caps Lock, Num Lock).

By maintaining this state inside a controller, we isolate typing heuristics from the raw data models.

---

## 2. Shift vs. Caps Lock
- **Shift (Temporary Lock)**: Toggles capitalization active for exactly **one** subsequent character.
  - *Heuristic*: Once the user types an alphanumeric key, the controller must auto-release the Shift lock (`self.shift_active = False`).
- **Caps Lock (Persistent Lock)**: Toggles capitalization active persistently until the user taps the key again.
- **Interlocking Rules**: Turning on Shift deactivates Caps Lock, and turning on Caps Lock deactivates Shift. This ensures predictable input behaviors.

---

## 3. Event Handling
Keystroke events are passed into the controller as logical string labels (e.g. `"Back"`, `"Space"`, `"Shift"`, `"Caps"`, `"A"`). The controller acts as the event dispatcher:

```
[Keystroke Event Signal] ──► KeyboardController.handle_keypress(label)
                                    │
          ┌─────────────────────────┼────────────────────────┐
          ▼ (Backspace)             ▼ (Modifier Toggle)      ▼ (Alphanumeric)
    Delete character          Toggle Shift/Caps Lock    Transform case & write
```

---

## 4. Business Logic Separation
By removing mapping rules from the buffer:
- **`TextBuffer` (Model)**: A pure, generic string data store. It only knows how to insert strings and delete characters. It does not know what a `"Shift"` key is.
- **`KeyboardController` (Presenter/Controller)**: Translates layout instructions into buffer actions.

This separation of concerns means that if we add text-manipulation utilities (e.g. text selection, cursor cursor movements, word wrap) later, we write them inside `TextBuffer` without modifying our layout mappings.

---

## 5. How this Mirrors Operating System Keyboard Pipelines
This design mirrors the standard driver-and-controller pipeline found in modern operating systems (such as macOS, Windows, and Linux):

1. **Hardware Keyboard Driver**: Captures mechanical key matrix closures and sends raw key scan codes (e.g., Scan Code `0x1E` for key 'A').
2. **OS Input Controller**: Receives scan codes and maintains active state registers (e.g. checking if the Shift key modifier is currently held down). It translates the scan code into an ASCII/Unicode character (e.g., 'a' if Shift is off, 'A' if Shift is on).
3. **Application Event Queue**: Receives the processed Unicode characters and appends them to active text fields or document buffers.

By replicating this pipeline structure, our virtual keyboard behaves exactly like a native physical keyboard, ensuring high reliability and modularity.
