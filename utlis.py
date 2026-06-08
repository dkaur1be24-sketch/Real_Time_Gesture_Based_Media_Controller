# =============================================================================
#  UTILS MODULE
#  All reusable UI drawing and visual helper functions for the
#  Gesture-Based Media Control System
#  Import this module wherever you need to draw on the video frame
# =============================================================================

import cv2
from datetime import datetime


# =============================================================================
#  TEXT RENDERING
# =============================================================================

def put_text(frame, text, position, color=(255, 255, 255), scale=0.6, thickness=2):
    """
    Render a text label onto a video frame.

    Parameters:
        frame     : The OpenCV video frame to draw on
        text      : The string to display
        position  : (x, y) pixel coordinates of the bottom-left of the text
        color     : BGR color tuple — default is white (255, 255, 255)
        scale     : Font size multiplier — default 0.6
        thickness : Stroke thickness in pixels — default 2

    Example:
        put_text(frame, "User #1 - ACTIVE", (20, 40), (0, 220, 80))
    """
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale, color, thickness
    )


def put_text_small(frame, text, position, color=(180, 180, 180)):
    """
    Render a smaller, thinner text label — used for secondary info
    like MAR values, finger counts, and status hints at the frame edges.

    Parameters:
        frame    : The OpenCV video frame to draw on
        text     : The string to display
        position : (x, y) pixel coordinates
        color    : BGR color tuple — default is light grey

    Example:
        put_text_small(frame, f"MAR: {mar:.2f}", (20, 460), (255, 230, 0))
    """
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45, color, 1
    )


def put_text_large(frame, text, position, color=(255, 255, 255)):
    """
    Render a larger, bolder text label — used for prominent alerts
    or section headers on the frame.

    Parameters:
        frame    : The OpenCV video frame to draw on
        text     : The string to display
        position : (x, y) pixel coordinates
        color    : BGR color tuple — default is white

    Example:
        put_text_large(frame, "FACE LOCKED", (20, 80), (0, 255, 120))
    """
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9, color, 2
    )


# =============================================================================
#  PROGRESS BAR
# =============================================================================

def draw_progress_bar(frame, value, max_value, x, y, w, h, color):
    """
    Draw a horizontal filled progress bar on the video frame.
    Used to show how close a held gesture is to triggering its action.

    Parameters:
        frame     : The OpenCV video frame to draw on
        value     : Current counter value (e.g., smile_counter = 18)
        max_value : Target value where the action fires (e.g., 25)
        x, y      : Top-left corner of the bar in pixels
        w, h      : Width and height of the bar in pixels
        color     : BGR fill color for the progress portion

    Visual:
        [ ████████████░░░░░░░░░ ]   (filled left to right)
        Grey outline shows the full bar width
        Colored fill shows current progress

    Example:
        draw_progress_bar(frame, smile_counter, 25, 20, 62, 220, 13, (0, 255, 120))
    """
    # Clamp value so the bar never overflows its boundary
    clamped  = min(value, max_value)
    progress = int((clamped / max_value) * w) if max_value > 0 else 0

    # Draw the grey outline (full bar background)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 1)

    # Draw the colored fill (progress so far)
    if progress > 0:
        cv2.rectangle(frame, (x, y), (x + progress, y + h), color, -1)


# =============================================================================
#  FACE BOUNDING BOX & NAME PILL
# =============================================================================

def draw_face_box(frame, x1, y1, x2, y2, label_text, box_color):
    """
    Draw a colored bounding box around a detected face with a
    pill-shaped name label above it.

    Parameters:
        frame      : The OpenCV video frame to draw on
        x1, y1     : Top-left corner of the face bounding box
        x2, y2     : Bottom-right corner of the face bounding box
        label_text : Text shown in the pill above the box
                     e.g., "User #1  [ACTIVE]" or "Stranger #2  [ignored]"
        box_color  : BGR color for both the box and the pill background
                     Green (0, 220, 80)  = authorized user
                     Blue  (0, 0, 220)   = unrecognized stranger

    Example:
        draw_face_box(frame, x1, y1, x2, y2,
                      "User #1  [ACTIVE]", (0, 220, 80))
    """
    # Draw the face bounding rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

    # Measure how wide the label text will be
    (tw, th), _ = cv2.getTextSize(
        label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1
    )

    # Position the pill just above the top of the bounding box
    pill_y1 = max(y1 - th - 10, 0)
    pill_y2 = max(y1 - 2, th + 4)

    # Draw the filled pill background
    cv2.rectangle(
        frame,
        (x1, pill_y1),
        (x1 + tw + 8, pill_y2),
        box_color, -1
    )

    # Draw the white label text inside the pill
    cv2.putText(
        frame, label_text,
        (x1 + 4, pill_y2 - 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52, (255, 255, 255), 1
    )


# =============================================================================
#  LIP LANDMARK DOTS
# =============================================================================

def draw_lip_landmarks(frame, face_landmarks, img_w, img_h):
    """
    Draw small green dots on the lip landmark points of the active user.
    Used to visually confirm that the MAR (smile) detection is tracking
    the correct facial features.

    Parameters:
        frame         : The OpenCV video frame to draw on
        face_landmarks: MediaPipe face mesh landmark object
        img_w         : Frame width in pixels
        img_h         : Frame height in pixels

    Example:
        draw_lip_landmarks(frame, face_lm, w, h)
    """
    # MediaPipe landmark IDs for the outer lip boundary
    lip_ids = [
        61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
        375, 321, 405, 314, 17, 84, 181, 91, 146
    ]

    for lid in lip_ids:
        lm   = face_landmarks.landmark[lid]
        px_x = int(lm.x * img_w)
        px_y = int(lm.y * img_h)
        cv2.circle(frame, (px_x, px_y), 1, (0, 220, 100), -1)


# =============================================================================
#  GESTURE LOG OVERLAY
# =============================================================================

def draw_gesture_log(frame, gesture_log, x, y):
    """
    Render the recent gesture history list as a semi-transparent
    overlay panel in the bottom-left corner of the frame.

    Parameters:
        frame       : The OpenCV video frame to draw on
        gesture_log : List of timestamped gesture event strings
                      e.g., ["[14:32:05] Smiled -> Playlist opened",
                              "[14:32:20] Open palm -> Volume UP"]
        x, y        : Top-left corner of the log panel

    Example:
        draw_gesture_log(frame, gesture_log, 20, h - 125)
    """
    if not gesture_log:
        return

    # Draw a solid black background panel behind the log text
    cv2.rectangle(
        frame,
        (x - 5,   y - 15),
        (x + 320, y + len(gesture_log) * 20 + 5),
        (0, 0, 0), -1
    )

    # Draw each log entry in light green
    for i, entry in enumerate(gesture_log):
        cv2.putText(
            frame, entry,
            (x, y + i * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38, (180, 255, 180), 1
        )


# =============================================================================
#  HUD TOP BAR
# =============================================================================

def draw_hud_bar(frame, frame_width, frame_height):
    """
    Draw the top black HUD bar with quick-reference gesture hints.
    This is the thin bar that runs across the very top of the video window.

    Parameters:
        frame        : The OpenCV video frame to draw on
        frame_width  : Width of the frame in pixels (w)
        frame_height : Height of the frame in pixels (h) — unused here
                       but kept for consistent function signature

    Example:
        draw_hud_bar(frame, w, h)
    """
    # Black bar background
    cv2.rectangle(frame, (0, 0), (frame_width, 22), (0, 0, 0), -1)

    # Gesture hint text
    cv2.putText(
        frame,
        "Smile=Play | Palm=Vol+ | Fist=Vol- | "
        "3=Pause | 4=Resume | Index=Next | V=Exit | Q=Quit",
        (6, 16),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.34, (180, 180, 180), 1
    )


# =============================================================================
#  GESTURE PROGRESS LABEL + BAR COMBO
#  Convenience function that draws both the label and the bar together
#  Used for every hold-based gesture in the main loop
# =============================================================================

def draw_gesture_indicator(frame, label, counter, max_frames, bar_y, label_y, color):
    """
    Draw a gesture progress indicator — a text label and a progress bar
    as a matched pair, stacked vertically on the left side of the frame.

    Parameters:
        frame      : The OpenCV video frame to draw on
        label      : Text to show above the bar
                     e.g., "3 Fingers - Pause (3/5)"
        counter    : Current hold-frame count
        max_frames : Frame count required to trigger the action
        bar_y      : Y pixel position of the progress bar
        label_y    : Y pixel position of the text label (usually bar_y - 4)
        color      : BGR color for both the label text and bar fill

    Example:
        draw_gesture_indicator(
            frame,
            f"3 Fingers - Pause ({three_finger_counter}/{PAUSE_FRAMES_REQUIRED})",
            three_finger_counter, PAUSE_FRAMES_REQUIRED,
            97, 93, (0, 200, 255)
        )
    """
    # Progress bar
    draw_progress_bar(frame, counter, max_frames, 20, bar_y, 220, 13, color)

    # Label text above the bar
    put_text(frame, label, (20, label_y), color, scale=0.55, thickness=1)


# =============================================================================
#  STATUS LINE
# =============================================================================

def draw_status_line(frame, active_user_id, is_active_in_frame):
    """
    Draw the status line just below the face bounding box area,
    showing whether the authorized user is currently visible and in control.

    Parameters:
        frame             : The OpenCV video frame to draw on
        active_user_id    : The name/label of the authorized user
        is_active_in_frame: True if the user's face was found this frame

    Example:
        draw_status_line(frame, "User #1", True)
    """
    if is_active_in_frame:
        put_text(frame,
                 f"{active_user_id} - controlling",
                 (20, 40), (0, 220, 80))
    else:
        put_text(frame,
                 f"{active_user_id} not in frame",
                 (20, 40), (0, 180, 255))


# =============================================================================
#  MAR DISPLAY
# =============================================================================

def draw_mar_value(frame, mar, threshold, frame_height):
    """
    Display the live Mouth Aspect Ratio (MAR) value and its threshold
    at the bottom of the frame for debugging and demonstration purposes.

    Parameters:
        frame        : The OpenCV video frame to draw on
        mar          : The current computed MAR value (float)
        threshold    : The MAR threshold from config (e.g., 1.8)
        frame_height : Frame height in pixels — used to position text

    Example:
        draw_mar_value(frame, active_mar, MAR_THRESHOLD, h)
    """
    put_text_small(
        frame,
        f"MAR: {mar:.2f}  (threshold > {threshold})",
        (20, frame_height - 15),
        (255, 230, 0)
    )


# =============================================================================
#  FINGER COUNT DISPLAY
# =============================================================================

def draw_finger_info(frame, finger_count, handedness, frame_height):
    """
    Display the detected finger count and hand side (Left / Right)
    near the bottom of the frame.

    Parameters:
        frame        : The OpenCV video frame to draw on
        finger_count : Number of fingers detected as extended (0–5)
        handedness   : "Left" or "Right" as returned by MediaPipe
        frame_height : Frame height in pixels — used to position text

    Example:
        draw_finger_info(frame, finger_count, handedness, h)
    """
    put_text_small(
        frame,
        f"Fingers: {finger_count}  Hand: {handedness}",
        (20, frame_height - 35),
        (200, 200, 255)
    )


# =============================================================================
#  NO DETECTION LABELS
# =============================================================================

def draw_no_face_label(frame):
    """
    Display a red warning label when no face is detected in the frame.

    Example:
        draw_no_face_label(frame)
    """
    put_text(frame, "No face detected", (20, 40), (0, 0, 255))


def draw_no_hand_label(frame, frame_width):
    """
    Display a grey label in the top-right corner when no hand is detected.

    Parameters:
        frame       : The OpenCV video frame to draw on
        frame_width : Frame width in pixels — used to right-align the label

    Example:
        draw_no_hand_label(frame, w)
    """
    put_text_small(
        frame,
        "No hand detected",
        (frame_width - 200, 40),
        (120, 120, 120)
    )


# =============================================================================
#  SMILE PROGRESS INDICATOR
# =============================================================================

def draw_smile_indicator(frame, smile_counter, smile_frames_required):
    """
    Draw the smile detection progress bar and label.
    Shown when the MAR threshold is exceeded and the smile counter
    is actively incrementing toward the trigger threshold.

    Parameters:
        frame                 : The OpenCV video frame to draw on
        smile_counter         : Current consecutive smile frame count
        smile_frames_required : Number of frames needed to trigger

    Example:
        draw_smile_indicator(frame, smile_counter, SMILE_FRAMES_REQUIRED)
    """
    draw_progress_bar(
        frame, smile_counter, smile_frames_required,
        20, 62, 220, 13, (0, 255, 120)
    )
    put_text(
        frame,
        f"Smiling... ({smile_counter}/{smile_frames_required})",
        (20, 58), (0, 255, 120), scale=0.5, thickness=1
    )
