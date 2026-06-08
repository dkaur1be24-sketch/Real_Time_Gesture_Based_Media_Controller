# =============================================================================
#  CONFIGURATION FILE
#  All tunable settings for the Gesture-Based Media Control System
#  Edit values here — no need to touch the main code
# =============================================================================


# =============================================================================
#  CAMERA SETTINGS
# =============================================================================

# Index of the webcam to use
# 0 = default/built-in camera | 1, 2... = external cameras
CAMERA_INDEX = 0


# =============================================================================
#  YOUTUBE SETTINGS
# =============================================================================

# Paste your YouTube video or playlist URL here
YOUTUBE_URL = "https://www.youtube.com/watch?v=xzUVPN68Ym4&list=PLTDo4oxuAZyTQ2qpHRvcCJX3gQHjubgqQ"


# =============================================================================
#  FACE RECOGNITION SETTINGS
# =============================================================================

# How strictly the system matches faces
# Lower value = stricter match (fewer false positives)
# Higher value = more lenient match (may accept strangers)
# Recommended range: 0.4 – 0.6
FACE_TOLERANCE = 0.5

# Re-compute face encoding every N frames for performance
# Higher = faster but slightly less accurate tracking
# Lower  = more accurate but heavier on CPU
ENCODING_INTERVAL = 10

# Label shown on screen for the authorized/locked user
ACTIVE_USER_ID = "User #1"


# =============================================================================
#  SMILE DETECTION SETTINGS
# =============================================================================

# Mouth Aspect Ratio threshold — how wide the mouth must open to count as smile
# Higher value = requires a bigger smile to trigger
# Lower value  = more sensitive, may trigger on slight mouth movements
MAR_THRESHOLD = 1.8

# Number of consecutive frames the smile must be held to trigger action
# Higher = less accidental triggers | Lower = responds faster
SMILE_FRAMES_REQUIRED = 25


# =============================================================================
#  GESTURE FRAME THRESHOLDS
#  Each gesture must be held for this many consecutive frames before firing.
#  Higher = more intentional but slower | Lower = faster but more accidental
# =============================================================================

# V-sign (✌️) held for this many frames → Exit program
VSIGN_FRAMES_REQUIRED = 10

# Index finger (☝️) held for this many frames → Skip to next song
INDEX_FRAMES_REQUIRED = 15

# Three fingers (3️⃣) held for this many frames → Pause song
PAUSE_FRAMES_REQUIRED = 5

# Four fingers (4️⃣) held for this many frames → Resume song
RESUME_FRAMES_REQUIRED = 5


# =============================================================================
#  COOLDOWN & LOCKOUT TIMERS (in seconds)
# =============================================================================

# Minimum time between volume UP / DOWN triggers
# Prevents repeated volume changes from a single held gesture
VOLUME_COOLDOWN = 1.2

# After pausing OR resuming, the opposite action is blocked for this duration.
# This prevents the hand naturally passing through the other gesture shape
# (e.g., 3-finger → 4-finger while lowering hand) from firing immediately.
# Recommended minimum: 2.5 seconds
PAUSE_RESUME_LOCKOUT = 3.0


# =============================================================================
#  FACE MESH LANDMARK INDICES
#  These are fixed MediaPipe landmark IDs used for Mouth Aspect Ratio (MAR)
#  Do not change unless you are remapping to different mouth points
# =============================================================================

MOUTH_LEFT   = 78    # left corner of the mouth
MOUTH_RIGHT  = 308   # right corner of the mouth
MOUTH_TOP    = 13    # top center of the upper lip
MOUTH_BOTTOM = 14    # bottom center of the lower lip


# =============================================================================
#  MEDIAPIPE MODEL SETTINGS
# =============================================================================

# --- Hands Model ---
MAX_NUM_HANDS             = 1     # track only 1 hand at a time
HAND_DETECTION_CONFIDENCE = 0.75  # minimum confidence to detect a hand
HAND_TRACKING_CONFIDENCE  = 0.60  # minimum confidence to keep tracking

# --- Face Mesh Model ---
MAX_NUM_FACES              = 4    # track up to 4 faces simultaneously
FACE_DETECTION_CONFIDENCE  = 0.5  # minimum confidence to detect a face
FACE_TRACKING_CONFIDENCE   = 0.5  # minimum confidence to keep tracking


# =============================================================================
#  BROWSER SETTINGS
# =============================================================================

# Brave browser executable paths (Windows)
# The system tries these in order and falls back to the default browser
BRAVE_PATHS = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
]

# Keywords used to find and focus the browser window
# Add your browser name here if it isn't listed
BROWSER_KEYWORDS = ["YouTube", "Chrome", "Firefox", "Edge", "Opera", "Brave"]

# Seconds to wait after opening the browser before trying to interact with it
# Increase this if the page hasn't loaded before playback starts
BROWSER_LOAD_WAIT = 5.0

# Where on screen to click to focus the YouTube video player
# 0.40 = 40% down from the top — targets the video frame area
# Adjust slightly if your screen layout puts the player elsewhere
PLAYER_CLICK_HEIGHT_RATIO = 0.40
