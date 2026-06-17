# 🎵 Gesture-Controlled YouTube Music Player

A Python-based intelligent music control system that allows users to control YouTube playback using **facial expressions** and **hand gestures** captured through a webcam.

The project combines **Computer Vision**, **Face Recognition**, **Hand Tracking**, **Gesture Recognition**, **Human-Computer Interaction (HCI)**, and **Automation** to create a touchless multimedia control experience.

---
## Demo Link
https://drive.google.com/file/d/1cHzdbKP9jMqYx5v461ocvJg1CVaETDIC/view?usp=sharing

## 📌 Features

### 😀 Face-Based Controls

* Detects and locks onto an authorized user's face.
* Uses facial recognition to prevent unauthorized users from controlling the system.
* Detects smile/open-mouth gestures using Mouth Aspect Ratio (MAR).
* Automatically launches a YouTube playlist when a smile is held for a specified duration.
* Captures and saves a screenshot when the playlist starts.

### ✋ Hand Gesture Controls

| Gesture               | Action                             |
| --------------------- | ---------------------------------- |
| Open Palm (5 Fingers) | Increase Volume                    |
| Closed Fist           | Decrease Volume                    |
| 3 Fingers             | Pause Music                        |
| 4 Fingers             | Resume Music                       |
| Index Finger Only     | Skip to Next Song                  |
| V-Sign                | Close Browser Tab and Exit Program |

### 🔊 Voice Feedback

* Text-to-Speech announcements for all major actions.
* Confirms system status and user commands through voice prompts.

### 📊 Real-Time Visual Feedback

* Live webcam feed.
* Face bounding boxes.
* Active user identification.
* Gesture progress bars.
* Finger count display.
* Action history log.
* Mouth Aspect Ratio (MAR) monitoring.

---

## 🏗️ System Architecture

1. Webcam captures live video frames.
2. Face Recognition identifies and locks onto the authorized user.
3. MediaPipe Face Mesh calculates Mouth Aspect Ratio (MAR).
4. Smile detection triggers YouTube playlist launch.
5. MediaPipe Hands detects hand landmarks.
6. Gesture classification determines user commands.
7. PyAutoGUI sends keyboard shortcuts to control YouTube.
8. Text-to-Speech engine provides audio feedback.
9. Action logs and visual indicators update in real time.

---

## 🛠️ Technologies Used

### Computer Vision

* OpenCV
* MediaPipe
* Face Recognition

### Automation

* PyAutoGUI
* PyGetWindow
* WebBrowser

### Voice Interaction

* pyttsx3

### Programming Language

* Python 3.x

---

## 📂 Project Structure

```text
Gesture-Controlled-YouTube-Player/
│
├── gesture_player.py
├── README.md
├── requirements.txt
├── smile_YYYYMMDD_HHMMSS.jpg
└── assets/
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/dkaur1be24-sketch/Real_Time_Gesture_Based_Media_Controller

cd Gesture-Controlled-YouTube-Player
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install opencv-python
pip install face-recognition
pip install mediapipe
pip install pyautogui
pip install pygetwindow
pip install pyttsx3
```

---

## ▶️ Usage

### Step 1

Open the source file 

```python
YOUTUBE_URL = "https://www.youtube.com/watch?v=xzUVPN68Ym4&list=PLTDo4oxuAZyTQ2qpHRvcCJX3gQHjubgqQ"
```

### Step 2

Run the program:

```bash
python gesture_player.py
```

### Step 3

Look at the webcam.

The system will:

* Detect your face.
* Lock onto the first recognized user.
* Wait for a smile gesture.

### Step 4

Hold a smile until the progress bar completes.

The system will:

* Open YouTube playlist.
* Start playback automatically.
* Save a screenshot.
* Announce the action through voice feedback.

### Step 5

Control music using hand gestures.

---

## 🎯 Gesture Reference

| Gesture      | Function                   |
| ------------ | -------------------------- |
| Smile        | Open Playlist + Screenshot |
| Open Palm    | Volume Up                  |
| Closed Fist  | Volume Down                |
| 3 Fingers    | Pause                      |
| 4 Fingers    | Resume                     |
| Index Finger | Next Song                  |
| V Sign       | Exit Program               |

---

## 🔒 Security Feature

The system uses face recognition to ensure only the authorized user can control playback.

Benefits:

* Prevents accidental gestures from other people.
* Supports multi-person environments.
* Improves interaction reliability.

---

## 📈 Future Enhancements

* Support for Spotify integration.
* Custom gesture training.
* Multiple user profiles.
* Deep learning-based gesture classification.
* Mobile application integration.
* Smart home device control.
* Voice command support.
* Emotion-aware music recommendation.

---

## 🎓 Learning Outcomes

This project demonstrates practical implementation of:

* Computer Vision
* Human-Computer Interaction (HCI)
* Face Recognition
* Gesture Recognition
* MediaPipe Hand Tracking
* OpenCV Video Processing
* Real-Time Automation
* Python GUI and System Control

---

## 👨‍💻 Author

Developed as a Computer Vision and Human-Computer Interaction project using Python, OpenCV, MediaPipe, and Face Recognition.

---

## 📜 License

This project is intended for educational and research purposes.
