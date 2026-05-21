TrainSight - Intelligent Agent for Exercise Technique Correction

**TrainSight** is a real-time intelligent agent that uses computer vision and pose estimation to analyze strength exercise technique through a camera. It detects joint angles, counts repetitions, and provides instant biomechanical feedback to help athletes improve their form and reduce injury risk.

Features
- Real-time Pose Detection** - MediaPipe Pose Landmarker for 33 body keypoints
- Joint Angle Analysis** - Automatic calculation of hip, knee, and back angles
- Exercise Support:
  -Squat analysis (`squat_rules.py`)
- Repetition Counter - Automatic rep counting with form validation
- Instant Feedback - Real-time visual and biomechanical cues
- State Trackin* - Exercise phase detection (ascent/descent)
- Movement Smoothing - Filtered pose data for stable tracking

Technologies
- Python 3.8+
- MediaPipe - Pose estimation
- OpenCV - Video capture and overlay
- NumPy - Mathematical computations

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
