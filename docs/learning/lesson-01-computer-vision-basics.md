# Learning Journal: Lesson 1 - Computer Vision Basics

## Date: 2026-07-07

### High-Level Introduction
Computer Vision (CV) is the field of study focused on enabling computers to gain high-level understanding from digital images or videos. In short, if AI allows computers to "think," CV allows them to "see."

For the **AirType** project, our goal is to translate visual landmarks on a human hand into physical typing inputs. This requires a strong foundation in digital image acquisition, matrix arithmetic, and real-time streaming pipelines.

### Common Tools in the Ecosystem
1. **OpenCV (Open Source Computer Vision Library)**: The industry standard library for image processing, camera access, and traditional computer vision algorithms.
2. **MediaPipe**: Google's open-source framework for building pipelines to process multi-modal sensory data. It provides pre-trained models for real-time face, hand, and pose tracking.
3. **NumPy**: The fundamental scientific computing library in Python. Because OpenCV represents images as multi-dimensional arrays, NumPy is critical for fast pixel-level mathematical operations.

### Image Coordinates System
Unlike classical cartesian math coordinate grids where the origin `(0,0)` is at the center or bottom-left, computer vision systems define coordinate grids starting at the **top-left corner**:
- **X-axis**: Increments from left to right (horizontal).
- **Y-axis**: Increments from top to bottom (vertical).

Understanding this spatial layout is critical for mapping fingertip landmarks to virtual coordinates of an on-screen keyboard layout.
