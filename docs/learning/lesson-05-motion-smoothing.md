# Learning Journal: Lesson 5 - Motion Smoothing with Exponential Moving Average

## Date: 2026-07-11

Today we introduced a modular coordinate filtering layer using an **Exponential Moving Average (EMA)** filter. We designed the filter system under a standard base interface to support the Open/Closed Principle.

---

## 1. What is Jitter?
In computer vision, **jitter** refers to high-frequency, rapid, and erratic fluctuations in coordinate values over sequential frames, even when the tracked object (in this case, a human finger) is held completely stationary in physical space.

---

## 2. Noise vs. Signal
- **Signal**: The true physical movement of the hand/fingertip. It resides in the low-frequency domain (human fingers cannot physically oscillate at 30 Hz).
- **Noise**: The high-frequency fluctuations caused by:
  - Sub-pixel lighting changes impacting neural network activation maps.
  - Camera sensor thermal noise.
  - Micro-tremors in human muscles.
  
To build a reliable typing interface, we must isolate and filter out the noise while preserving the true signal.

---

## 3. Why Smoothing is Necessary
If we map raw coordinates directly to a virtual keyboard:
- The virtual cursor will shake erratically, making it difficult for the user to target specific keys (especially small letters like 'I' or 'O').
- The system will experience high rate of false clicks (tap triggers) if the tap classification is distance-dependent, as noise values can cause coordinates to jump below threshold metrics.
- The interface will feel cheap and fatiguing to use.

---

## 4. Smoothing Algorithms Comparison

| Feature | Moving Average (MA) | Exponential Moving Average (EMA) | Kalman Filter | One Euro Filter |
| :--- | :--- | :--- | :--- | :--- |
| **Memory Cost** | High (Requires queue of size $N$) | **Minimal** (Requires single state float) | Moderate (Requires covariance matrices) | Minimal (Requires velocity & state) |
| **CPU Cycles** | Low | **Extremely Low** | High (Matrix calculations) | Low (Multi-step calculation) |
| **Adaptability** | Fixed window | Fixed weights | Dynamically updates based on noise | Dynamically updates based on velocity |
| **Complexity** | Simple | **Simple** | High | Moderate |

- **Kalman Filter**: Extremely robust but computationally heavy. It assumes Gaussian noise distributions and requires constructing transition and measurement covariance matrices, which adds overhead for a simple 2D cursor.
- **One Euro Filter**: An adaptive filter designed for human-computer interaction. It uses a dynamic cutoff frequency that decreases when velocity is low (to reduce jitter) and increases when velocity is high (to reduce lag). It is a strong candidate for future implementation.
- **Exponential Moving Average (EMA)**: Offers the best ratio of simplicity to performance. It is extremely fast, uses minimal memory, and provides clean smoothing curves for steady signals.

---

## 5. Mathematical Formulation of EMA
EMA computes a weighted average of the current coordinate and all previous coordinate histories:
\[S_t = \alpha \times Y_t + (1 - \alpha) \times S_{t-1}\]
Where:
- \(S_t\): Smoothed coordinate at time step \(t\).
- \(Y_t\): Raw coordinate measurement at time step \(t\).
- \(S_{t-1}\): Previous step's smoothed coordinate output.
- \(\alpha\): Smoothing coefficient constant (\(0 < \alpha \le 1.0\)).

---

## 6. Responsiveness vs. Stability Trade-off
The behavior of the EMA filter is governed entirely by the parameter \(\alpha\):
- **High \(\alpha\) (e.g., 0.8)**: Prioritizes **responsiveness**. The output tracks the raw coordinates closely. There is almost zero lag, but sensor jitter is still visible.
- **Low \(\alpha\) (e.g., 0.1)**: Prioritizes **stability**. The cursor is extremely steady, but it lags behind fast hand movements with a "rubber-band" trailing delay.

For AirType, a value of **\(\alpha = 0.3\)** represents the optimal middle ground: it filters out high-frequency sensor noise while keeping input latency below the threshold of human noticeability (~20-30ms).

---

## 7. How AirType Uses Smoothed Coordinates
1. **Targeting Cursor**: The virtual cursor is locked to `smoothed_pixel_coords` to ensure steady, pixel-perfect targeting over letters.
2. **Lag Tracking Vector**: By comparing `pixel_coords` (raw) and `smoothed_pixel_coords` (smoothed), the visualizer draws a vector line representing hand speed and direction. This can be used to dynamically adapt tap detection parameters (e.g., locking key selections if velocity is high to prevent slide-typing errors).
3. **Tracking Reset**: When MediaPipe loses tracking, the filter history is reset. This ensures that when the hand re-enters the camera frame, the smoothed cursor instantly locks onto the new position rather than animating smoothly from the last coordinates recorded before the hand left.
