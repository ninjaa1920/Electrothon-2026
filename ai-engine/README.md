# Women Safety Analytics - AI Engine

This module serves as the core intelligence of the system, utilizing a hybrid model approach for real-time video analytics.

## 🧠 Model Architecture & Logic

### 1. Person Detection
- **Model**: **YOLOv8** (Ultralytics).
- **Purpose**: High-speed detection of all individuals in the frame.

### 2. Gender Classification
- **Model**: **VGG16** (Pre-trained on ImageNet).
- **Implementation**: Fine-tuned using **PyTorch** on custom gender classification datasets.
- **Flow**: Detected person crops from YOLO -> VGG16 -> Male/Female class.

### 3. Risk Analysis (Contextual)
- **Primary Logic**: **Coordinate-based Distance Analysis**.
    - Calculate Euclidean distances between centroids of detected persons.
    - Logic: `Risk = f(Distance, Count, Gender Ratio)`.
- **Advanced Logic (Lone Woman/Surrounded)**:
    - **Thermal Mapping**: Simulating thermal intensity or using thermal feed if available.
    - **Pixel Difference**: Using **OpenCV** to detect motion intensity and density around the subject.
    - **Scenario**: If *One Woman* + *Search/Pixel Density High* + *Late Night* = **High Risk**.

### 4. SOS Gesture Detection
- **Library**: **MediaPipe Hands**.
- **Triggers**: 
    - "Open Palm" (Stop gesture).
    - Specific dynamic gestures (e.g., Fist Clench).

## 🛠️ Tech Stack
- **Languages**: Python 3.8+
- **Frameworks**: PyTorch, Ultralytics YOLO, MediaPipe.
- **Libraries**: OpenCV (Pixel logic), NumPy (Coordinates), Socket.io (Alerts).

## Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to install `torch` and `torchvision` separately depending on your CUDA version).*

2.  Run the engine:
    ```bash
    python main.py
    ```

## Development Notes
- **VGG16 Fine-tuning**: Ensure the model weights are saved in a `weights/` directory.
- **Alerts**: Generative content (Gemini) can be integrated for describing the alert context textually before sending to Backend.
