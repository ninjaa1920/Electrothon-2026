import cv2
import socketio
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
import threading
import time
import requests

# Initialize Socket.IO client
sio = socketio.Client()

# Initialize MediaPipe Hands for SOS detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # Using nano model for speed

# Global variables
current_alert_level = "Low"
frame_count = 0
backend_url = 'http://localhost:3000'

def connect_socket():
    try:
        sio.connect(backend_url)
        print("Connected to backend via Socket.IO")
    except Exception as e:
        print(f"Socket connection failed: {e}")
        # Retry logic could be added here

def send_alert(alert_data):
    try:
        # Emit via socket for real-time dashboard
        if sio.connected:
            sio.emit('new_alert', alert_data)
        
        # Post to API for persistence
        requests.post(f'{backend_url}/api/alert', json=alert_data)
        print(f"Alert sent: {alert_data['riskLevel']}")
    except Exception as e:
        print(f"Failed to send alert: {e}")

def detect_sos(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    sos_detected = False
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Simple heuristic: Open palm (fingers extended) to fist (fingers closed)
            # For simplicity in this demo, we'll check for a specific "Stop" gesture (open palm) as a proxy or "Fist"
            # Getting state of fingers (Open/Closed)
            fingers = []
            
            # Thumb
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)
            
            # 4 Fingers
            for id in range(8, 21, 4):
                if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # SOS Logic: If explicit open palm (5) or fist (0) is held for a duration, or a specific transition
            # Here we detect "Open Palm" (5 fingers up) which is often used as "Stop" or "Help" in some contexts,
            # or we can check for the "Signal for Help" (Palm in, Thumb in, Fingers over) - complex to script perfectly in a hurry.
            # Let's use Open Palm = High Alert for demo purposes or specific SOS Logic.
            
            # Detect Fist (0 fingers) as potential threat/distress or aggressive behavior? 
            # Let's say: 
            # 5 Fingers Open = Low/Safe (Waving) - actually context dependent.
            
            # Let's implement a "Fist" detection as SOS for this specific hackathon requirement if requested, 
            # OR better: The "Signal for Help" is: 1. Palm to camera, 2. Tuck thumb, 3. Trap thumb.
            
            # Simplified for MVP: Function detects if hand is raised and fingers are open (5) -> Safe/Wave, 
            # If hand is raised and fist (0) -> Warning?
            
            # Re-reading prompt: "Gesture Detection: ... specific hand landmarks (e.g., raised palm/fist) will be used for SOS."
            # Let's trigger SOS on a specific stable gesture, e.g., "Open Palm" held up.
            
            if sum(fingers) == 5:
                return True
                
    return sos_detected

def analyze_risk(people_boxes, classes, frame):
    global current_alert_level
    
    person_count = 0
    men_count = 0
    women_count = 0
    risk_level = "Low"
    description = "Normal activity"
    
    centroids = []
    
    for box, cls in zip(people_boxes, classes):
        if int(cls) == 0: # Person class in YOLO
            person_count += 1
            x1, y1, x2, y2 = box
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            centroids.append((cx, cy))
            
            # Gender Classification Placeholder
            # extracting face/body ROI would go here
            # For hackathon MVP, we might simulate or randomise if model not trained
            # simulation: Randomly assign for demo if no secondary model
            # OR simple heuristic based on appearance IS HARD without model
            # Let's assume a simplified logic or use a mock for "men/women" distribution
            # to verify the RISK LOGIC.
            
            # For this code, I will simply count all persons. 
            # To actually demo "Lone Woman", we need gender. 
            # I will add a mock function or property to 'people' for now 
            # since a real gender model is heavy to load in single script without weights.
            # We'll assume the user might want to test this logic.
            
            # If we really need it, we'd use a second small CNN. 
            # Let's proceed with logic Assuming we have gender.
            pass

    # Basic Risk Logic (Placeholder without real gender)
    # If 1 person (Woman) and Night -> High Risk
    # If 1 Woman + 4 Men closely surrounding -> Critical
    
    # Implementing Proximity Logic
    if len(centroids) > 2:
        # Calculate distances
        distances = []
        for i in range(len(centroids)):
            for j in range(i + 1, len(centroids)):
                dist = np.linalg.norm(np.array(centroids[i]) - np.array(centroids[j]))
                distances.append(dist)
        
        if len(distances) > 0 and min(distances) < 100: # Threshold for "close"
            risk_level = "Medium"
            description = "Crowd forming / High Proximity"

    # SOS Override
    if detect_sos(frame):
        risk_level = "Critical"
        description = "SOS Gesture Detected"
        
    return {
        "timestamp": time.time(),
        "riskLevel": risk_level,
        "description": description,
        "location": "Camera_01"
    }

def main():
    connect_socket()
    cap = cv2.VideoCapture(0) # Webcam
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # YOLO Detection
        results = model(frame, stream=True)
        
        boxes = []
        classes = []
        
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()
            
            # Draw boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Risk Analysis
        alert_data = analyze_risk(boxes, classes, frame)
        
        # Display Status
        cv2.putText(frame, f"Risk: {alert_data['riskLevel']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Send Alert if Level High/Critical
        if alert_data['riskLevel'] in ["High", "Critical"]:
            # Throttling could be added here
            threading.Thread(target=send_alert, args=(alert_data,)).start()

        cv2.imshow("Woman Safety Analytics", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    sio.disconnect()

if __name__ == '__main__':
    main()
