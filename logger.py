# =============================================================================
#  LOGGER MODULE
#  Handles all logging for the Gesture-Based Media Control System
#  Logs are written to system.log and printed to console simultaneously
# =============================================================================

import logging
import os
from datetime import datetime


# =============================================================================
#  LOG FILE CONFIGURATION
#  All logs are saved to system.log in the same folder as the script
# =============================================================================

# Build the full path to the log file (same directory as this script)
LOG_FOLDER   = os.path.dirname(os.path.abspath(__file__))
LOG_FILENAME = os.path.join(LOG_FOLDER, "system.log")

# Maximum log file size before it gets overwritten on next run
# Set to None to keep appending forever across sessions
LOG_MODE = "a"   # "a" = append to existing log | "w" = overwrite on each run


# =============================================================================
#  LOGGER SETUP
#  Two handlers:
#    1. FileHandler  — writes everything to system.log
#    2. StreamHandler — mirrors INFO+ logs to the console
# =============================================================================

# Create a named logger specific to this project
logger = logging.getLogger("GestureMediaControl")
logger.setLevel(logging.DEBUG)   # capture everything DEBUG and above

# Prevent duplicate log entries if this module is imported multiple times
if not logger.handlers:

    # ------------------------------------------------------------------
    #  Handler 1: File — writes all levels to system.log
    # ------------------------------------------------------------------
    file_handler = logging.FileHandler(LOG_FILENAME, mode=LOG_MODE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s  |  %(levelname)-8s  |  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # ------------------------------------------------------------------
    #  Handler 2: Console — prints INFO and above to terminal
    # ------------------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# =============================================================================
#  SESSION SEPARATOR
#  Writes a visible divider into the log file each time the program starts
#  Makes it easy to tell sessions apart when reviewing system.log
# =============================================================================

def log_session_start():
    """
    Write a session start banner to the log file.
    Call this once at the very beginning of the program.

    Output in system.log:
        ============================================================
        SESSION STARTED — 2025-06-08 14:32:01
        ============================================================
    """
    separator = "=" * 60
    logger.info(separator)
    logger.info(f"SESSION STARTED — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(separator)


def log_session_end():
    """
    Write a session end banner to the log file.
    Call this just before the program exits.

    Output in system.log:
        SESSION ENDED — 2025-06-08 14:45:17
        ============================================================
    """
    logger.info(f"SESSION ENDED   — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60 + "\n")


# =============================================================================
#  GENERAL PURPOSE LOG FUNCTION
#  Drop-in replacement for your original log_event(message)
# =============================================================================

def log_event(message):
    """
    Log a general INFO-level event.
    This is the main function used throughout the project.

    Parameters:
        message (str): The event description to log.

    Example:
        log_event("Face locked for User #1")
        → [14:32:05] INFO     Face locked for User #1
        → written to system.log
    """
    logger.info(message)


# =============================================================================
#  LEVEL-SPECIFIC LOG FUNCTIONS
#  Use these for more precise logging throughout the main file
# =============================================================================

def log_info(message):
    """
    Log a standard informational message.
    Use for normal system events (model loaded, camera started, etc.)

    Example:
        log_info("MediaPipe models loaded successfully.")
    """
    logger.info(message)


def log_debug(message):
    """
    Log a detailed debug message (only appears in system.log, not console).
    Use for low-level values like MAR readings, frame counts, finger states.

    Example:
        log_debug(f"MAR value this frame: {mar:.4f}")
    """
    logger.debug(message)


def log_warning(message):
    """
    Log a warning — something unexpected happened but the system continues.
    Use for browser focus failures, missing windows, fallback triggers, etc.

    Example:
        log_warning("Brave not found — falling back to default browser.")
    """
    logger.warning(message)


def log_error(message):
    """
    Log an error — something failed that may affect system behavior.
    Use for camera open failures, file save errors, etc.

    Example:
        log_error("Cannot open camera at index 0.")
    """
    logger.error(message)


def log_critical(message):
    """
    Log a critical failure — the system cannot continue.
    Use just before a forced exit.

    Example:
        log_critical("Face recognition model failed to load. Exiting.")
    """
    logger.critical(message)


# =============================================================================
#  GESTURE-SPECIFIC LOG FUNCTIONS
#  Clean one-liners for every gesture action in the main file
#  Each writes a consistently formatted INFO entry to system.log
# =============================================================================

def log_face_locked(user_id):
    """Logged when the first face is detected and locked as authorized user."""
    log_event(f"FACE LOCKED      — {user_id} is now in control.")

def log_face_reset():
    """Logged when the R key resets the face lock."""
    log_event("FACE RESET       — Face lock cleared. Awaiting new user.")

def log_smile_play(url):
    """Logged when a smile triggers the YouTube playlist to open."""
    log_event(f"GESTURE: SMILE   — Playlist opened: {url}")

def log_screenshot(filename):
    """Logged when a smile screenshot is saved."""
    log_event(f"SCREENSHOT       — Saved: {filename}")

def log_volume_up():
    """Logged when open palm raises the volume."""
    log_event("GESTURE: PALM    — Volume UP triggered.")

def log_volume_down():
    """Logged when closed fist lowers the volume."""
    log_event("GESTURE: FIST    — Volume DOWN triggered.")

def log_pause():
    """Logged when 3-finger gesture pauses the song."""
    log_event("GESTURE: 3 FINGERS — Song PAUSED.")

def log_resume():
    """Logged when 4-finger gesture resumes the song."""
    log_event("GESTURE: 4 FINGERS — Song RESUMED.")

def log_next_song():
    """Logged when index-finger gesture skips to the next song."""
    log_event("GESTURE: INDEX   — Skipped to NEXT song.")

def log_exit():
    """Logged when V-sign gesture triggers program exit."""
    log_event("GESTURE: V-SIGN  — Exit triggered. Closing tab and shutting down.")

def log_browser_focused(keyword):
    """Logged when the browser window is successfully brought to foreground."""
    log_debug(f"BROWSER FOCUS    — Window found via keyword: '{keyword}'")

def log_browser_not_found():
    """Logged when no browser window could be located."""
    log_warning("BROWSER FOCUS    — No browser window found to activate.")

def log_playback_started():
    """Logged when the startup click + keypress sequence completes."""
    log_event("PLAYBACK         — Player clicked and K sent. Playback started.")

def log_camera_error():
    """Logged when the webcam cannot be opened."""
    log_error("CAMERA           — Cannot open webcam. Check CAMERA_INDEX in config.py.")

def log_fps(fps):
    """Logged periodically to track real-time performance."""
    log_debug(f"PERFORMANCE      — Current FPS: {fps:.2f}")

def log_mar(mar):
    """Logged every frame for the active user's Mouth Aspect Ratio value."""
    log_debug(f"MAR VALUE        — {mar:.4f}  (threshold: {1.8})")

def log_inference_time(action_name, inference_time):
    """Logged after each gesture fires to record its dispatch time."""
    log_debug(f"INFERENCE        — '{action_name}' dispatched in {inference_time:.4f} sec")
