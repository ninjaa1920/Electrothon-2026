import cv2
import socketio
import time
import threading
import requests
from ultralytics import YOLO

from modules.gender import GenderClassifier
from modules.risk import RiskEngine
from modules.sos import SOSDetector

# Configuration
BACKEND_URL = 'http://localhost:3000'
YOLO_MODEL_PATH = 'yolov8n.pt' # Standard YOLOv8 Nano

class AIEngine:
    def __init__(self):
        print("Initializing AI Engine...")
        
        # 1. Connect to Backend
        self.sio = socketio.Client()
        self.connect_socket()

        # 2. Load Models
        self.yolo = YOLO(YOLO_MODEL_PATH)
        self.gender_classifier = GenderClassifier() # Loads VGG16
        self.risk_engine = RiskEngine()
        self.sos_detector = SOSDetector()
        
        self.running = True
        
    def connect_socket(self):
        try:
            self.sio.connect(BACKEND_URL)
            print(f"✅ Connected to Backend at {BACKEND_URL}")
        except Exception as e:
            print(f"⚠️ Socket Connection Failed: {e}")

    def send_alert(self, alert_data):
        """Sends alert logic via Socket.IO"""
        if self.sio.connected:
            self.sio.emit('new_alert', alert_data)
            print(f"🚀 Alert Sent: {alert_data['riskLevel']}")
        else:
            # Try to reconnect or log
            pass

    def run(self):
        cap = cv2.VideoCapture(0) # 0 for Webcam
        
        while self.running:
            ret, frame = cap.read()
            if not ret: break

            # --- A. SOS Detection (Result determines if we need Critical Alert immediately) ---
            is_sos, hand_landmarks = self.sos_detector.detect(frame)
            
            if is_sos:
                alert_data = {
                    "timestamp": time.time(),
                    "riskLevel": "Critical",
                    "description": "SOS Gesture Detected (Open Palm)",
                    "location": "Camera_01" 
                }
                self.send_alert(alert_data)
                cv2.putText(frame, "SOS DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # --- B. Person Detection & Attribute Extraction ---
            results = self.yolo(frame, stream=True, verbose=False)
            people_data = []

            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy()
                
                for box, cls in zip(boxes, classes):
                    if int(cls) == 0: # Person
                        x1, y1, x2, y2 = map(int, box)
                        
                        # Crop Face/Body for Gender
                        # Basic logic: Crop upper body or assume whole person crop is enough
                        # VGG16 expects 224x224
                        person_crop = frame[y1:y2, x1:x2]
                        if person_crop.size > 0:
                            gender = self.gender_classifier.predict(person_crop)
                        else:
                            gender = "Unknown"
                        
                        # Store Metadata
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        people_data.append({
                            "box": [x1, y1, x2, y2],
                            "centroid": (cx, cy),
                            "gender": gender
                        })
                        
                        # Draw Basic Visuals
                        color = (255, 100, 100) if gender == "Female" else (100, 255, 100)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, gender, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # --- C. Risk Analysis ---
            if not is_sos: # Only run detailed risk if not already Critical SOS
                risk_result = self.risk_engine.analyze(people_data, frame)
                
                if risk_result['riskLevel'] in ['High', 'Critical']:
                     alert_data = {
                        "timestamp": time.time(),
                        "riskLevel": risk_result['riskLevel'],
                        "description": risk_result['description'],
                        "location": "Camera_01"
                    }
                     self.send_alert(alert_data)

                # Visuals
                cv2.putText(frame, f"Risk: {risk_result['riskLevel']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

            cv2.imshow("AI Engine - Eyes That Anticipate", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
        
        cap.release()
        cv2.destroyAllWindows()
        self.sio.disconnect()


if __name__ == '__main__':
    engine = AIEngine()
    engine.run()
