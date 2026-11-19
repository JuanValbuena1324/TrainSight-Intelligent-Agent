# 🏋️ TrainSight - Intelligent Agent for Exercise Technique Correction

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose_Landmarker-0097A7?style=flat&logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=flat&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Biomechanics-013243?style=flat&logo=numpy&logoColor=white)
![AI Agent](https://img.shields.io/badge/Architecture-Goal--Based_Agent-10B981?style=flat)

## Description

**TrainSight** is a real-time intelligent agent designed for strength exercise technique correction using computer vision and pose estimation. Through live camera capture, the agent perceives body movement, tracks internal state and memory, evaluates biomechanical rules, counts valid repetitions, and delivers instant visual feedback to help athletes improve their squat form and reduce injury risk.

## Authors

| Contributor | Role / Focus |
| :--- | :--- |
| Juan Pablo Valbuena | `Intelligent Agent Architecture, Pose Estimation & Biomechanical Rules` |

## Agent Architecture & Core Features

* **Goal-Based & Model-Based Agent Design:** Structured separation between perception (`capture.py`, `pose.py`), internal world state (`agent_model.py`, `state_tracker.py`), short/long-term session history (`agent_memory.py`), target objectives (`agent_goals.py`), and decision-making (`agent.py`).
* **Real-Time Pose Estimation:** Powered by **MediaPipe Pose Landmarker** (`pose_landmarker_full.task`) to extract 33 3D body keypoints in real time.
* **Signal Smoothing:** Temporal filtering (`smoother.py`) to reduce landmark jitter and stabilize joint tracking.
* **Biomechanical Joint Angle Analysis:** Vector-based computation (`angles.py`) of hip, knee, and torso inclination angles.
* **Rule-Based Form Evaluation:** Modular exercise validation (`rules/squat_rules.py`) that detects execution phases (standing, descent, bottom, ascent) and flags posture errors.
* **Automated Repetition Counter & Visual HUD:** Real-time overlay (`overlay.py`) displaying angles, phase state, rep count, and corrective cues directly over the video stream.

## Project Structure

```text
TrainSight-Intelligent-Agent/
├── main.py                      # Application entry point and main execution loop
├── config.py                    # Thresholds, camera settings, and biomechanical parameters
├── agent.py                     # Core intelligent agent decision-making orchestrator
├── agent_model.py               # Internal representation of the athlete's current state
├── agent_goals.py               # Target biomechanical goals and form criteria
├── agent_memory.py              # Session history, rep logs, and performance tracking
├── capture.py                   # Real-time webcam video capture handler
├── pose.py                      # MediaPipe Pose Landmarker wrapper
├── smoother.py                  # Coordinate filtering and movement smoothing
├── angles.py                    # Trigonometric joint angle calculations
├── state_tracker.py             # Finite state machine for exercise phases (ascent/descent)
├── overlay.py                   # OpenCV HUD rendering for visual feedback
├── pose_landmarker_full.task    # Pre-trained MediaPipe pose detection model
├── requirements.txt             # Python dependencies
├── memory/                      # Stored session logs and agent memory data
└── rules/
    └── squat_rules.py           # Biomechanical rules and thresholds for squat analysis

Installation

```bash
# Clone repository
git clone https://github.com/JuanValbuena1324/TrainSight-Intelligent-Agent.git
cd TrainSight-Intelligent-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
