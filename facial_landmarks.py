# =============================================================================
#  GESTURE-CONTROLLED YOUTUBE MUSIC PLAYER
#  Uses webcam to detect face expressions and hand gestures to control music
# =============================================================================

import cv2
import face_recognition
import mediapipe as mp
import webbrowser
import pyautogui
import pygetwindow as gw
import pyttsx3
import time
import os
from datetime import datetime


# =============================================================================
#  CONFIGURATION CONSTANTS
#  Tweak these values to adjust sensitivity and behavior
# =============================================================================

# Paste your YouTube playlist URL here
YOUTUBE_URL = "https://www.youtube.com/watch?v=xzUVPN68Ym4&list=PLTDo4oxuAZyTQ2qpHRvcCJX3gQHjubgqQ"

# How wide the mouth must open (ratio) to count as a smile/open mouth
MAR_THRESHOLD = 1.8

# Number of consecutive frames each gesture must be held to trigger action
SMILE_FRAMES_REQUIRED  = 25   # frames to hold smile  -> opens playlist
VSIGN_FRAMES_REQUIRED  = 10   # frames to hold V-sign -> exits program
INDEX_FRAMES_REQUIRED  = 15   # frames to hold index  -> skips to next song
PAUSE_FRAMES_REQUIRED  = 5    # frames to hold 3 fingers -> pauses song
RESUME_FRAMES_REQUIRED = 5    # frames to hold 4 fingers -> resumes song

# Cooldown in seconds between volume changes (palm / fist)
VOLUME_COOLDOWN = 1.2

# After pausing OR resuming, block the opposite action for this many seconds.
# This prevents the hand naturally passing through 4-finger shape (while
# lowering after a 3-finger pause) from instantly triggering a resume.
PAUSE_RESUME_LOCKOUT = 3.0

# Face-recognition settings
MATCH_TOLERANCE   = 0.5   # lower = stricter face match
ENCODING_INTERVAL = 10    # re-compute face encoding every N frames (performance)

# Label shown on screen for the authorized user
ACTIVE_USER_ID = "User #1"

# Folder where smile screenshots are saved (same folder as this script)
SCREENSHOT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# MediaPipe FaceMesh landmark indices used for mouth-open detection
MOUTH_LEFT   = 78
MOUTH_RIGHT  = 308
MOUTH_TOP    = 13
MOUTH_BOTTOM = 14


# =============================================================================
#  TEXT-TO-SPEECH ENGINE SETUP
# =============================================================================

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160)    # speaking speed (words per minute)
tts_engine.setProperty('volume', 1.0)  # volume (0.0 – 1.0)

def speak(text):
    """Speak a message aloud and print it to the console."""
    print(f"[TTS] {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()


# =============================================================================
#  MEDIAPIPE MODEL INITIALIZATION
#  Hand tracking + Face mesh (landmarks for mouth & face box)
# =============================================================================

print("[INFO] Loading models...")

mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Hand tracking model — detects up to 1 hand at a time
hands_model = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.6
)

mp_face_mesh = mp.solutions.face_mesh

# Face mesh model — detects up to 4 faces, used for mouth ratio & bounding box
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=4,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

print("[INFO] Models loaded.")


# =============================================================================
#  HELPER FUNCTIONS — FACE
# =============================================================================

def mouth_aspect_ratio(landmarks, img_w, img_h):
    """
    Calculate the Mouth Aspect Ratio (MAR).
    MAR = horizontal width / vertical height of the mouth opening.
    A large MAR means the mouth is open wide (smile / yawn).
    """
    def px(lm_idx):
        lm = landmarks.landmark[lm_idx]
        return int(lm.x * img_w), int(lm.y * img_h)

    lx, ly = px(MOUTH_LEFT)
    rx, ry = px(MOUTH_RIGHT)
    tx, ty = px(MOUTH_TOP)
    bx, by = px(MOUTH_BOTTOM)

    width  = ((rx - lx) ** 2 + (ry - ly) ** 2) ** 0.5
    height = ((bx - tx) ** 2 + (by - ty) ** 2) ** 0.5
    return (width / height) if height != 0 else 0


# =============================================================================
#  HELPER FUNCTIONS — HAND GESTURE DETECTION
# =============================================================================

def count_fingers(hand_landmarks, handedness_label):
    """
    Count how many fingers are extended and return a boolean list.
    Returns: (total_count, [thumb, index, middle, ring, pinky])
    Each entry is True if that finger is raised, False if curled.
    """
    lm   = hand_landmarks.landmark
    tips = [8, 12, 16, 20]   # fingertip landmark IDs
    pips = [6, 10, 14, 18]   # middle-joint landmark IDs

    # A finger is up if its tip is higher (smaller y) than its middle joint
    fingers = [lm[t].y < lm[p].y for t, p in zip(tips, pips)]

    # Thumb uses x-axis direction (mirrored for left vs right hand)
    if handedness_label == "Right":
        thumb_up = lm[4].x < lm[3].x
    else:
        thumb_up = lm[4].x > lm[3].x

    fingers = [thumb_up] + fingers   # prepend thumb to the list
    return sum(fingers), fingers


def is_open_palm(finger_count, fingers):
    """All 5 fingers extended — Volume UP."""
    return finger_count == 5


def is_closed_fist(finger_count, fingers):
    """All fingers (except thumb) curled — Volume DOWN."""
    return not any(fingers[1:])


def is_v_sign(finger_count, fingers):
    """Index + middle only (peace sign) — Exit program."""
    thumb, index, middle, ring, pinky = fingers
    return (index and middle) and (not ring) and (not pinky) and (not thumb)


def is_index_only(finger_count, fingers):
    """Only index finger extended — Skip to next song."""
    thumb, index, middle, ring, pinky = fingers
    return index and (not thumb) and (not middle) and (not ring) and (not pinky)


def is_three_fingers(finger_count, fingers):
    """
    Index + middle + ring extended, thumb and pinky down — Pause song.
    Checked explicitly to avoid confusion with 4-finger or open-palm shapes.
    """
    thumb, index, middle, ring, pinky = fingers
    return (finger_count == 3
            and index and middle and ring
            and not thumb and not pinky)


def is_four_fingers(finger_count, fingers):
    """
    Index + middle + ring + pinky extended, thumb tucked — Resume song.
    Thumb must be down to distinguish from open palm (5 fingers).
    """
    thumb, index, middle, ring, pinky = fingers
    return (finger_count == 4
            and index and middle and ring and pinky
            and not thumb)


# =============================================================================
#  HELPER FUNCTIONS — UI DRAWING
# =============================================================================

def draw_progress_bar(frame, value, maximum, x, y, w, h, color):
    """Draw a filled progress bar that shows how close a gesture is to firing."""
    progress = int((min(value, maximum) / maximum) * w)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 1)
    if progress > 0:
        cv2.rectangle(frame, (x, y), (x + progress, y + h), color, -1)


def put_label(frame, text, pos, color=(255, 255, 255), scale=0.6, thickness=2):
    """Convenience wrapper for cv2.putText."""
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)


# =============================================================================
#  HELPER FUNCTIONS — ACTIONS
# =============================================================================

def take_screenshot(frame):
    """Save the current frame as a JPEG and return the filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"smile_{timestamp}.jpg"
    filepath  = os.path.join(SCREENSHOT_FOLDER, filename)
    cv2.imwrite(filepath, frame)
    print(f"[SCREENSHOT] Saved: {filepath}")
    return filename


def focus_browser():
    """
    Bring the browser window to the foreground so pyautogui keypresses
    are received by YouTube rather than the OpenCV window.
    Returns True if a browser window was found and activated.
    """
    browser_keywords = ["YouTube", "Chrome", "Firefox", "Edge", "Opera", "Brave"]
    for keyword in browser_keywords:
        windows = gw.getWindowsWithTitle(keyword)
        if windows:
            try:
                windows[0].activate()
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"[WARN] Could not activate window: {e}")
    return False


def close_browser_tab():
    """
    Destroy the OpenCV window first (so the script doesn't freeze),
    then close the active browser tab with Ctrl+W.
    """
    cv2.destroyAllWindows()
    time.sleep(0.3)
    found = focus_browser()
    if found:
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.3)
        print("[ACTION] Browser tab closed.")
    else:
        print("[WARN] No browser window found to close.")


def start_youtube_playback():
    """
    Reliably start YouTube playback after the page loads.

    YouTube opens with the video PAUSED by default waiting for a real
    user interaction. This function:
      1. Waits for the page to fully render (5 seconds)
      2. Clicks the video player area to give it keyboard focus
      3. Moves the mouse away so the control bar auto-hides
      4. Sends 'k' (YouTube play/pause toggle) to begin playback
      5. Sends a safety Tab + second 'k' in case an overlay (cookie
         banner, ad, autoplay dialog) stole focus after the first press
    """
    # Give the page enough time to fully load — 5s handles slow connections
    time.sleep(5)

    if focus_browser():
        screen_w, screen_h = pyautogui.size()

        # Target the video player frame: center-x, 40% down the screen.
        # This lands on the video itself rather than the description or
        # recommendations that sit in the lower half of the page.
        player_x = screen_w // 2
        player_y = int(screen_h * 0.40)

        # Click to focus the player area
        pyautogui.click(player_x, player_y)
        time.sleep(0.8)   # wait for focus to fully settle

        # Move mouse to the bottom of the screen so the YouTube control
        # bar auto-hides and doesn't interfere with playback
        pyautogui.moveTo(player_x, screen_h - 50)
        time.sleep(0.3)

        # First 'k' press — should start playback now that the player
        # has focus. YouTube was paused, so one toggle = play.
        pyautogui.press('k')
        time.sleep(0.4)

        # Safety net: if a cookie banner, ad-skip button, or autoplay
        # overlay stole focus, Tab moves past it and the second 'k'
        # reaches the player.
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('k')

        print("[ACTION] Player clicked and K sent (with safety fallback).")


# =============================================================================
#  GESTURE LOG — small on-screen history of recent actions
# =============================================================================

gesture_log = []   # stores the last 5 gesture events

def log_gesture(message):
    """Add a timestamped entry to the on-screen gesture log."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry     = f"[{timestamp}] {message}"
    gesture_log.append(entry)
    if len(gesture_log) > 5:
        gesture_log.pop(0)   # keep only the 5 most recent entries
    print(f"[LOG] {entry}")


def draw_gesture_log(frame, log, x, y):
    """Render the gesture history list onto the video frame."""
    cv2.rectangle(frame,
                  (x - 5,   y - 15),
                  (x + 320, y + len(log) * 20 + 5),
                  (0, 0, 0), -1)
    for i, entry in enumerate(log):
        cv2.putText(frame, entry,
                    (x, y + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.38, (180, 255, 180), 1)


# =============================================================================
#  STATE VARIABLES
#  All mutable state that changes frame-to-frame lives here
# =============================================================================

# Face recognition state
locked_encoding = None   # encoding of the authorized user's face
last_encoding   = None   # most recently computed encoding (cached)

# Smile / playlist state
smile_counter    = 0
youtube_opened   = False
screenshot_taken = False

# Gesture frame counters
vsign_counter        = 0
index_counter        = 0
three_finger_counter = 0   # counts consecutive frames of 3-finger gesture
four_finger_counter  = 0   # counts consecutive frames of 4-finger gesture

# Cooldown timestamps — track when each action last fired
last_volume_time = 0
last_next_time   = 0
last_pause_time  = 0

# Treat startup as "just resumed" so the 3-finger pause gesture is
# immediately available without waiting for PAUSE_RESUME_LOCKOUT to expire.
# If this were 0, the lockout check (now - last_resume_time > 3.0) would
# fail for the first 3 seconds and block the very first pause attempt.
last_resume_time = time.time()

# General frame counter (used to throttle face-encoding computation)
frame_count = 0


# =============================================================================
#  CAMERA SETUP
# =============================================================================

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot open camera.")
    exit()

print("[INFO] Camera started.")
print("-" * 49)
print("  GESTURE REFERENCE:")
print("  Smile (hold 25f)     -> Play YouTube + Screenshot")
print("  Open palm            -> Volume UP")
print("  Closed fist          -> Volume DOWN")
print("  3 Fingers (hold 5f)  -> Pause song")
print("  4 Fingers (hold 5f)  -> Resume song")
print("  Index only (hold 15f)-> Next song")
print("  V-sign (hold 10f)    -> Close tab + Exit")
print("-" * 49)
print("  Press R to reset face lock | Press Q to quit")

speak("System ready. Smile to play music.")


# =============================================================================
#  MAIN LOOP
# =============================================================================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame = cv2.flip(frame, 1)                        # mirror so it feels natural
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # MediaPipe expects RGB
    h, w  = frame.shape[:2]

    # ------------------------------------------------------------------
    #  FACE RECOGNITION — identify and lock onto the authorized user
    # ------------------------------------------------------------------

    # Work on a half-size image for speed; coordinates scale back automatically
    small          = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
    face_locations = face_recognition.face_locations(small)

    all_encodings = []
    if face_locations:
        # Only re-compute encodings every ENCODING_INTERVAL frames
        if frame_count % ENCODING_INTERVAL == 0:
            all_encodings = face_recognition.face_encodings(small, face_locations)
            if all_encodings:
                last_encoding = all_encodings[0]
        else:
            # Reuse the last known encoding between computation frames
            if last_encoding is not None:
                all_encodings = [last_encoding] + [None] * (len(face_locations) - 1)

    # First face seen becomes the locked/authorized user
    if locked_encoding is None and all_encodings and all_encodings[0] is not None:
        locked_encoding = all_encodings[0]
        print(f"[INFO] {ACTIVE_USER_ID} locked.")
        speak("Face locked. You are in control.")

    # ------------------------------------------------------------------
    #  FACE MESH — draw landmarks, bounding boxes, and compute MAR
    # ------------------------------------------------------------------

    mesh_result      = face_mesh.process(rgb)
    active_mar       = None
    active_box_drawn = False

    if mesh_result.multi_face_landmarks:
        for idx, face_lm in enumerate(mesh_result.multi_face_landmarks):

            # Compute bounding box from all landmark positions
            xs = [lm.x for lm in face_lm.landmark]
            ys = [lm.y for lm in face_lm.landmark]
            x1 = max(int(min(xs) * w), 0)
            y1 = max(int(min(ys) * h), 0)
            x2 = min(int(max(xs) * w), w)
            y2 = min(int(max(ys) * h), h)

            # Check whether this face matches the locked user
            is_active = False
            if locked_encoding is not None and idx < len(all_encodings):
                enc = all_encodings[idx]
                if enc is not None:
                    is_active = face_recognition.compare_faces(
                        [locked_encoding], enc, tolerance=MATCH_TOLERANCE
                    )[0]

            # Color-code the bounding box: green = active user, blue = stranger
            if is_active:
                box_color  = (0, 220, 80)
                label_text = f"{ACTIVE_USER_ID}  [ACTIVE]"
            else:
                box_color  = (0, 0, 220)
                label_text = (f"Stranger #{idx+1}  [ignored]"
                              if locked_encoding is not None else "Identifying...")

            # Draw bounding box and name pill
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            pill_y1 = max(y1 - th - 10, 0)
            pill_y2 = max(y1 - 2,  th + 4)
            cv2.rectangle(frame, (x1, pill_y1), (x1 + tw + 8, pill_y2), box_color, -1)
            cv2.putText(frame, label_text,
                        (x1 + 4, pill_y2 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

            # Only run mouth/smile detection for the active (authorized) user
            if is_active:

                # Draw lip landmark dots
                lip_ids = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
                           375, 321, 405, 314, 17, 84, 181, 91, 146]
                for lid in lip_ids:
                    lm   = face_lm.landmark[lid]
                    px_x = int(lm.x * w)
                    px_y = int(lm.y * h)
                    cv2.circle(frame, (px_x, px_y), 1, (0, 220, 100), -1)

                # Compute Mouth Aspect Ratio for smile detection
                mar        = mouth_aspect_ratio(face_lm, w, h)
                active_mar = mar

                if mar > MAR_THRESHOLD:
                    # Mouth is open — increment smile counter
                    smile_counter += 1
                    draw_progress_bar(frame, smile_counter,
                                      SMILE_FRAMES_REQUIRED,
                                      20, 62, 220, 13, (0, 255, 120))
                    put_label(frame,
                              f"Smiling... ({smile_counter}/{SMILE_FRAMES_REQUIRED})",
                              (20, 58), (0, 255, 120), 0.5)

                    # Trigger: open YouTube playlist after holding smile long enough
                    if smile_counter >= SMILE_FRAMES_REQUIRED and not youtube_opened:

                        # Try Brave first; fall back to the system default browser
                        brave_paths = [
                            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                        ]
                        opened = False
                        for brave_path in brave_paths:
                            if os.path.exists(brave_path):
                                webbrowser.register('brave', None,
                                    webbrowser.BackgroundBrowser(brave_path))
                                webbrowser.get('brave').open(YOUTUBE_URL)
                                opened = True
                                break
                        if not opened:
                            print("[WARN] Brave not found — using default browser.")
                            webbrowser.open(YOUTUBE_URL)

                        # Start playback using the dedicated function.
                        # This waits for the page to load, clicks the player,
                        # and sends 'k' with a safety fallback (see function above).
                        start_youtube_playback()

                        youtube_opened = True
                        log_gesture("Smiled -> Playlist opened")
                        speak("Playing your playlist.")

                        # Take a one-time smile screenshot
                        if not screenshot_taken:
                            filename = take_screenshot(frame)
                            screenshot_taken = True
                            log_gesture(f"Screenshot -> {filename}")
                            speak("Screenshot saved.")
                else:
                    # Mouth closed — reset smile state
                    smile_counter    = 0
                    youtube_opened   = False
                    screenshot_taken = False

                active_box_drawn = True

        # Status line below the face box
        if active_box_drawn:
            put_label(frame, f"{ACTIVE_USER_ID} - controlling", (20, 40), (0, 220, 80))
        else:
            smile_counter = 0
            put_label(frame, f"{ACTIVE_USER_ID} not in frame", (20, 40), (0, 180, 255))

        # Show live MAR value at the bottom of the frame
        if active_mar is not None:
            put_label(frame,
                      f"MAR: {active_mar:.2f}  (threshold > {MAR_THRESHOLD})",
                      (20, h - 15), (255, 230, 0), 0.45, 1)
    else:
        # No faces detected at all
        smile_counter = 0
        put_label(frame, "No face detected", (20, 40), (0, 0, 255))


    # ------------------------------------------------------------------
    #  HAND GESTURE DETECTION
    # ------------------------------------------------------------------

    hand_result = hands_model.process(rgb)
    now         = time.time()

    if hand_result.multi_hand_landmarks:
        hand_lm    = hand_result.multi_hand_landmarks[0]
        handedness = hand_result.multi_handedness[0].classification[0].label

        # Draw hand skeleton on the frame
        mp_drawing.draw_landmarks(
            frame, hand_lm, mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(80, 200, 255), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(200, 80, 255), thickness=2)
        )

        finger_count, fingers = count_fingers(hand_lm, handedness)

        # --------------------------------------------------------------
        #  GESTURE: OPEN PALM (5 fingers) — Volume UP
        # --------------------------------------------------------------
        if is_open_palm(finger_count, fingers):
            draw_progress_bar(frame, 1, 1, 20, 97, 220, 13, (0, 210, 255))
            put_label(frame, "Open palm - Volume UP", (20, 93), (0, 210, 255), 0.55)

            if now - last_volume_time > VOLUME_COOLDOWN:
                pyautogui.press('volumeup')
                pyautogui.press('volumeup')
                last_volume_time = now
                log_gesture("Open palm -> Volume UP")
                speak("Volume up.")

            # Reset all hold-counters since this is a different gesture
            vsign_counter        = 0
            index_counter        = 0
            three_finger_counter = 0
            four_finger_counter  = 0

        # --------------------------------------------------------------
        #  GESTURE: 3 FINGERS (index + middle + ring) — Pause song
        #
        #  LOCKOUT: Also checks that at least PAUSE_RESUME_LOCKOUT seconds
        #  have passed since the last RESUME, so a hand naturally passing
        #  through 3-finger shape right after resuming won't re-pause.
        # --------------------------------------------------------------
        elif is_three_fingers(finger_count, fingers):
            three_finger_counter += 1
            four_finger_counter   = 0   # reset the opposing gesture counter

            draw_progress_bar(frame, three_finger_counter,
                              PAUSE_FRAMES_REQUIRED,
                              20, 97, 220, 13, (0, 200, 255))
            put_label(frame,
                      f"3 Fingers - Pause ({three_finger_counter}/{PAUSE_FRAMES_REQUIRED})",
                      (20, 93), (0, 200, 255), 0.55)

            # Fire only when:
            #   1. Held for enough frames
            #   2. Regular cooldown since last pause has passed
            #   3. Lockout since last RESUME has passed (prevents accidental re-pause)
            if (three_finger_counter >= PAUSE_FRAMES_REQUIRED
                    and now - last_pause_time  > VOLUME_COOLDOWN
                    and now - last_resume_time > PAUSE_RESUME_LOCKOUT):
                focus_browser()
                pyautogui.press('k')   # YouTube keyboard shortcut: toggle play/pause
                last_pause_time      = now
                three_finger_counter = 0
                log_gesture("3 Fingers -> Paused")
                speak("Paused.")

            vsign_counter = 0
            index_counter = 0

        # --------------------------------------------------------------
        #  GESTURE: 4 FINGERS (index+middle+ring+pinky, thumb tucked) — Resume song
        #
        #  LOCKOUT: Also checks that at least PAUSE_RESUME_LOCKOUT seconds
        #  have passed since the last PAUSE, so a hand passing through 4-finger
        #  shape while lowering after a 3-finger pause won't instantly resume.
        # --------------------------------------------------------------
        elif is_four_fingers(finger_count, fingers):
            four_finger_counter  += 1
            three_finger_counter  = 0   # reset the opposing gesture counter

            draw_progress_bar(frame, four_finger_counter,
                              RESUME_FRAMES_REQUIRED,
                              20, 127, 220, 13, (255, 100, 50))
            put_label(frame,
                      f"4 Fingers - Resume ({four_finger_counter}/{RESUME_FRAMES_REQUIRED})",
                      (20, 123), (255, 100, 50), 0.55)

            # Fire only when:
            #   1. Held for enough frames
            #   2. Regular cooldown since last resume has passed
            #   3. Lockout since last PAUSE has passed (prevents accidental instant resume)
            if (four_finger_counter  >= RESUME_FRAMES_REQUIRED
                    and now - last_resume_time > VOLUME_COOLDOWN
                    and now - last_pause_time  > PAUSE_RESUME_LOCKOUT):
                focus_browser()
                pyautogui.press('k')   # YouTube keyboard shortcut: toggle play/pause
                last_resume_time    = now
                four_finger_counter = 0
                log_gesture("4 Fingers -> Resumed")
                speak("Resumed.")

            vsign_counter = 0
            index_counter = 0

        # --------------------------------------------------------------
        #  GESTURE: CLOSED FIST (no fingers) — Volume DOWN
        # --------------------------------------------------------------
        elif is_closed_fist(finger_count, fingers):
            draw_progress_bar(frame, 1, 1, 20, 157, 220, 13, (255, 140, 0))
            put_label(frame, "Closed fist - Volume DOWN", (20, 153), (255, 140, 0), 0.55)

            if now - last_volume_time > VOLUME_COOLDOWN:
                pyautogui.press('volumedown')
                pyautogui.press('volumedown')
                last_volume_time = now
                log_gesture("Closed fist -> Volume DOWN")
                speak("Volume down.")

            vsign_counter        = 0
            index_counter        = 0
            three_finger_counter = 0
            four_finger_counter  = 0

        # --------------------------------------------------------------
        #  GESTURE: INDEX FINGER ONLY — Next song (hold to confirm)
        # --------------------------------------------------------------
        elif is_index_only(finger_count, fingers):
            index_counter += 1
            draw_progress_bar(frame, index_counter,
                              INDEX_FRAMES_REQUIRED,
                              20, 187, 220, 13, (0, 255, 200))
            put_label(frame,
                      f"Index finger - Next song ({index_counter}/{INDEX_FRAMES_REQUIRED})",
                      (20, 183), (0, 255, 200), 0.5)

            if (index_counter >= INDEX_FRAMES_REQUIRED
                    and now - last_next_time > 2.0):
                focus_browser()
                pyautogui.hotkey('shift', 'n')   # YouTube: skip to next video
                last_next_time       = now
                index_counter        = 0
                log_gesture("Index finger -> Next song")
                speak("Next song.")

            vsign_counter        = 0
            three_finger_counter = 0
            four_finger_counter  = 0

        # --------------------------------------------------------------
        #  GESTURE: V-SIGN (index + middle) — Hold to exit program
        # --------------------------------------------------------------
        elif is_v_sign(finger_count, fingers):
            vsign_counter += 1
            draw_progress_bar(frame, vsign_counter,
                              VSIGN_FRAMES_REQUIRED,
                              20, 187, 220, 13, (80, 80, 255))
            put_label(frame,
                      f"V-sign - Hold to EXIT ({vsign_counter}/{VSIGN_FRAMES_REQUIRED})",
                      (20, 183), (120, 120, 255), 0.5)

            if vsign_counter >= VSIGN_FRAMES_REQUIRED:
                log_gesture("V-sign -> Closing tab + Exit")

                # Step 1: Release camera and models cleanly
                cap.release()
                hands_model.close()
                face_mesh.close()

                # Step 2: Close the browser tab playing music
                close_browser_tab()   # also calls cv2.destroyAllWindows()

                # Step 3: Say goodbye via Windows PowerShell SAPI
                # (used instead of pyttsx3 because cv2/mediapipe are already closed)
                import subprocess
                ps_cmd = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$s.Rate = 1; "
                    "$s.Speak('Thank you for your time, we hope you enjoyed it.');"
                )
                subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                # Step 4: Exit the program
                exit()

            index_counter        = 0
            three_finger_counter = 0
            four_finger_counter  = 0

        # --------------------------------------------------------------
        #  NO RECOGNIZED GESTURE — reset all hold-counters
        # --------------------------------------------------------------
        else:
            vsign_counter        = 0
            index_counter        = 0
            three_finger_counter = 0
            four_finger_counter  = 0

        # Show finger count and hand side at the bottom of frame
        put_label(frame,
                  f"Fingers: {finger_count}  Hand: {handedness}",
                  (20, h - 35), (200, 200, 255), 0.45, 1)

    else:
        # No hand in frame — reset all counters
        vsign_counter        = 0
        index_counter        = 0
        three_finger_counter = 0
        four_finger_counter  = 0
        put_label(frame, "No hand detected", (w - 200, 40), (120, 120, 120), 0.5, 1)


    # ------------------------------------------------------------------
    #  ON-SCREEN GESTURE LOG & HUD BAR
    # ------------------------------------------------------------------

    if gesture_log:
        draw_gesture_log(frame, gesture_log, 20, h - 125)

    # Top black bar with quick-reference gesture hints
    cv2.rectangle(frame, (0, 0), (w, 22), (0, 0, 0), -1)
    put_label(frame,
              "Smile=Play | Palm=Vol+ | Fist=Vol- | 3=Pause | 4=Resume | Index=Next | V=Exit | Q=Quit",
              (6, 16), (180, 180, 180), 0.34, 1)

    cv2.imshow("Gesture Control", frame)

    # ------------------------------------------------------------------
    #  KEYBOARD CONTROLS
    # ------------------------------------------------------------------

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        # Q key — quit the program immediately
        print("[INFO] Quit by user.")
        break

    elif key == ord('r'):
        # R key — reset face lock so a new person can become the active user
        locked_encoding      = None
        last_encoding        = None
        smile_counter        = 0
        vsign_counter        = 0
        index_counter        = 0
        three_finger_counter = 0
        four_finger_counter  = 0
        youtube_opened       = False
        screenshot_taken     = False
        frame_count          = 0
        gesture_log.clear()
        speak("Face lock reset.")
        print("[INFO] Face lock reset.")


# =============================================================================
#  CLEANUP — release all resources when the loop exits
# =============================================================================

cap.release()
cv2.destroyAllWindows()
hands_model.close()
face_mesh.close()
print("[INFO] Goodbye.")
