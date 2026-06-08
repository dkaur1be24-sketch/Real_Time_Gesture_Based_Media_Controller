# =============================================================================
#  INFERENCE MODULE
#  Handles action execution timing, FPS logging, and performance tracking
#  for the Gesture-Based Media Control System
# =============================================================================

import time
from datetime import datetime


# =============================================================================
#  PERFORMANCE TRACKER
#  Keeps a running history of inference times and FPS readings
#  so you can review system performance at any point
# =============================================================================

# Stores the last N inference time records
inference_history = []

# Stores the last N FPS readings
fps_history = []

# How many records to keep in memory at a time
MAX_HISTORY_LENGTH = 50


# =============================================================================
#  ACTION EXECUTION TIMER
# =============================================================================

def run_inference(action_name):
    """
    Measures and logs the time taken to trigger a gesture action.

    In this system, 'inference' refers to the moment a gesture is
    confirmed and the corresponding action is dispatched (e.g., sending
    a keypress to the browser, adjusting volume, taking a screenshot).

    Parameters:
        action_name (str): Human-readable name of the action being triggered.
                           e.g., "Pause", "Volume UP", "Next Song", "Exit"

    Returns:
        float: Time taken to execute the action dispatch, in seconds.

    Example:
        inference_time = run_inference("Pause")
        → [ACTION TRIGGERED]: Pause
        → [INFERENCE TIME]: 0.0023 sec
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Record start time just before the action fires
    start = time.time()

    print(f"[{timestamp}] [ACTION TRIGGERED]: {action_name}")

    # Record end time immediately after
    end = time.time()

    inference_time = end - start

    print(f"[{timestamp}] [INFERENCE TIME]: {inference_time:.4f} sec")

    # Store in history for performance review
    _record_inference(action_name, inference_time, timestamp)

    return inference_time


# =============================================================================
#  FPS LOGGER
# =============================================================================

def log_fps(fps):
    """
    Logs the current frames-per-second reading of the webcam loop.

    Called once per second (or at any interval you choose) from the
    main loop to track how smoothly the system is running.

    Parameters:
        fps (float): Current FPS value computed in the main loop.

    Example:
        log_fps(27.4)
        → [FPS]: 27.40
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] [FPS]: {fps:.2f}")

    # Store in history
    fps_history.append({
        "timestamp": timestamp,
        "fps":       round(fps, 2)
    })

    # Keep history from growing indefinitely
    if len(fps_history) > MAX_HISTORY_LENGTH:
        fps_history.pop(0)


# =============================================================================
#  PERFORMANCE SUMMARY
# =============================================================================

def print_performance_summary():
    """
    Prints a summary of inference times and FPS collected during the session.

    Call this at the end of the program (before exit) to get an overview
    of how the system performed across all gesture triggers.

    Output example:
        ── PERFORMANCE SUMMARY ──────────────────────
        Total actions triggered : 12
        Average inference time  : 0.0018 sec
        Fastest inference time  : 0.0004 sec  (Volume UP)
        Slowest inference time  : 0.0041 sec  (Exit)
        Average FPS             : 24.83
        Lowest FPS              : 19.20
        Highest FPS             : 29.70
        ─────────────────────────────────────────────
    """
    print("\n" + "─" * 45)
    print("  PERFORMANCE SUMMARY")
    print("─" * 45)

    # --- Inference stats ---
    if inference_history:
        times      = [r["inference_time"] for r in inference_history]
        avg_time   = sum(times) / len(times)
        min_record = min(inference_history, key=lambda r: r["inference_time"])
        max_record = max(inference_history, key=lambda r: r["inference_time"])

        print(f"  Total actions triggered : {len(inference_history)}")
        print(f"  Average inference time  : {avg_time:.4f} sec")
        print(f"  Fastest inference time  : {min_record['inference_time']:.4f} sec"
              f"  ({min_record['action']})")
        print(f"  Slowest inference time  : {max_record['inference_time']:.4f} sec"
              f"  ({max_record['action']})")
    else:
        print("  No actions were triggered this session.")

    # --- FPS stats ---
    if fps_history:
        fps_values = [r["fps"] for r in fps_history]
        avg_fps    = sum(fps_values) / len(fps_values)
        min_fps    = min(fps_values)
        max_fps    = max(fps_values)

        print(f"  Average FPS             : {avg_fps:.2f}")
        print(f"  Lowest FPS              : {min_fps:.2f}")
        print(f"  Highest FPS             : {max_fps:.2f}")
    else:
        print("  No FPS readings recorded this session.")

    print("─" * 45 + "\n")


# =============================================================================
#  GESTURE-SPECIFIC WRAPPERS
#  Each gesture action has its own named wrapper so the main file
#  can call clean one-liners instead of passing strings manually.
#  These also make the action log easier to read.
# =============================================================================

def infer_smile_play():
    """Triggered when smile gesture opens the YouTube playlist."""
    return run_inference("Smile → Play Playlist")

def infer_volume_up():
    """Triggered when open palm raises the volume."""
    return run_inference("Open Palm → Volume UP")

def infer_volume_down():
    """Triggered when closed fist lowers the volume."""
    return run_inference("Closed Fist → Volume DOWN")

def infer_pause():
    """Triggered when 3-finger gesture pauses the song."""
    return run_inference("3 Fingers → Pause")

def infer_resume():
    """Triggered when 4-finger gesture resumes the song."""
    return run_inference("4 Fingers → Resume")

def infer_next_song():
    """Triggered when index-finger gesture skips to the next song."""
    return run_inference("Index Finger → Next Song")

def infer_exit():
    """Triggered when V-sign gesture exits the program."""
    return run_inference("V-Sign → Exit")

def infer_screenshot():
    """Triggered when a smile screenshot is automatically saved."""
    return run_inference("Smile → Screenshot Saved")


# =============================================================================
#  INTERNAL HELPER
# =============================================================================

def _record_inference(action_name, inference_time, timestamp):
    """
    Internal function — stores an inference record in the history list.
    Not intended to be called directly from outside this module.
    """
    inference_history.append({
        "timestamp":      timestamp,
        "action":         action_name,
        "inference_time": round(inference_time, 6)
    })

    # Keep history from growing indefinitely
    if len(inference_history) > MAX_HISTORY_LENGTH:
        inference_history.pop(0)
