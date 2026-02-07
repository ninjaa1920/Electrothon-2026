import cv2
import socketio
import time
import threading
import requests
import torch
from ultralytics import YOLO
import mediapipe as mp
import os
import numpy as np
from collections import deque, Counter

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from modules.gender import GenderClassifier
from modules.risk import RiskEngine
from modules.sos import SOSDetector

# Configuration
BACKEND_URL = 'http://localhost:3000'
YOLO_MODEL_PATH = 'yolov8n.pt' # Standard YOLOv8 Nano

# LOCATION CONFIGURATION (Hardcoded for Laptop/Camera 1)
LATITUDE = 28.644800  
LONGITUDE = 77.216721
LOCATION_NAME = "Camera_01"

class AIEngine:
    def __init__(self):
        print("Initializing AI Engine...")
        
        # 1. Connect to Backend
        self.sio = socketio.Client()
        self.connect_socket()

        # 2. Load Models
        self.yolo = YOLO(YOLO_MODEL_PATH)
        self.gender_classifier = GenderClassifier(weights_path='vgg16_gender.pth') # Loads VGG16
        self.risk_engine = RiskEngine()
        self.sos_detector = SOSDetector()
        
        self.gender_memory = {} # Locks gender prediction per ID
        self.gender_vote_buffer = {} # ID -> deque(maxlen=7)
        # 3. Face Detector (MediaPipe Tasks API)
        fd_model_path = 'blaze_face_short_range.tflite'
        if not os.path.exists(fd_model_path):
             print(f"Downloading Face Detector model to {fd_model_path}...")
             import urllib.request
             url = 'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite'
             try:
                 urllib.request.urlretrieve(url, fd_model_path)
                 print("Download complete.")
             except Exception as e:
                 print(f"Failed to download Face Detector: {e}")

        try:
            base_options = python.BaseOptions(model_asset_path=fd_model_path)
            options = vision.FaceDetectorOptions(base_options=base_options, min_detection_confidence=0.5)
            self.face_detector = vision.FaceDetector.create_from_options(options)
            print("✅ Face Detector Initialized")
        except Exception as e:
            print(f"❌ Failed to init Face Detector: {e}")
            self.face_detector = None
        
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
                    "location": LOCATION_NAME,
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE
                }
                self.send_alert(alert_data)
                cv2.putText(frame, "SOS DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # --- B. Person Detection & Attribute Extraction ---
            # Use .track() to persist IDs with higher confidence to reduce ghosts
            results = self.yolo.track(frame, persist=True, verbose=False, conf=0.5) 
            people_data = []

            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy()
                
                # Check if we have IDs (tracking might miss in first frame)
                ids = r.boxes.id.cpu().numpy() if r.boxes.id is not None else [-1] * len(boxes)
                
                for box, cls, track_id in zip(boxes, classes, ids):
                    if int(cls) == 0: # Person
                        x1, y1, x2, y2 = map(int, box)
                        track_id = int(track_id)

                        # Aspect Ratio Check (Person should be taller than wide)
                        w = x2 - x1
                        h = y2 - y1
                        if w > h * 1.2: # If width is 20% larger than height, it's likely an object (sofa/bed)
                             continue
                        
                        # Crop Face/Body for Gender
                        person_crop = frame[y1:y2, x1:x2]
                        

                            
                        # 1. Try to detect face in the person crop using MP Tasks
                        face_img = None
                        if self.face_detector and person_crop.size > 0:
                            try:
                                # Convert to MP Image
                                rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                                rgb_crop = np.array(rgb_crop, dtype=np.uint8) # FORCE UINT8 for mp
                                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_crop)
                                
                                detection_result = self.face_detector.detect(mp_image)
                                
                                if detection_result.detections:
                                    # Get first face
                                    detection = detection_result.detections[0]
                                    bbox = detection.bounding_box
                                    
                                    # BBox is relative to person_crop
                                    fx = bbox.origin_x
                                    fy = bbox.origin_y
                                    fw = bbox.width
                                    fh = bbox.height
                                    
                                    # Ensure bounds
                                    ih, iw, _ = person_crop.shape
                                    fx, fy = max(0, fx), max(0, fy)
                                    fw, fh = min(iw - fx, fw), min(ih - fy, fh)
                                    
                                    if fw > 0 and fh > 0:
                                        face_img = person_crop[fy:fy+fh, fx:fx+fw]
                                        
                                        # 0. Min Size Check (Avoid blurry faces)
                                        # DEBUG PRINT
                                        # print(f"ID {track_id}: Face Size {fw}x{fh}") 
                                        
                                        if fw < 50 or fh < 50:
                                            # print(f"Skipping ID {track_id}: Face too small")
                                            continue

                                        # Only predict if we have a FACE
                                        pred_gender, conf = self.gender_classifier.predict(face_img)
                                        
                                        # DEBUG PRINT
                                        # print(f"ID {track_id}: Raw Pred {pred_gender} ({conf:.2f})")

                                        # Consensus Voting Logic
                                        if conf > 0.70:
                                            if track_id not in self.gender_vote_buffer:
                                                self.gender_vote_buffer[track_id] = deque(maxlen=7)
                                            
                                            self.gender_vote_buffer[track_id].append(pred_gender)

                                            # Check for Consensus (Need at least 5 votes)
                                            if len(self.gender_vote_buffer[track_id]) >= 5:
                                                counts = Counter(self.gender_vote_buffer[track_id])
                                                most_common, count = counts.most_common(1)[0]
                                                
                                                # If > 70% agree, LOCK it
                                                if count / len(self.gender_vote_buffer[track_id]) > 0.7:
                                                     self.gender_memory[track_id] = most_common
                                            
                                        # DEBUG: Save Face to check quality
                                        if (int(time.time() * 10)) % 30 == 0:
                                                os.makedirs("debug_faces", exist_ok=True)
                                                cv2.imwrite(f"debug_faces/face_{track_id}_{int(time.time())}_{pred_gender}.jpg", face_img)

                            except Exception as e:
                                print(f"Face Det Error: {e}")

                        # Retrieve from Memory (or Unknown)
                        final_gender = self.gender_memory.get(track_id, "Unknown")

                        # Store Metadata
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        people_data.append({
                            "box": [x1, y1, x2, y2],
                            "centroid": (cx, cy),
                            "gender": final_gender,
                            "id": track_id
                        })
                        
                        # Draw Basic Visuals
                        color = (255, 100, 100) if final_gender == "Female" else (100, 255, 100)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # DEBUG: Save Face to check quality
                        if face_img is not None and face_img.size > 0:
                             # Save every 30th frame to avoid spamming
                             if (int(time.time() * 10)) % 30 == 0:
                                 os.makedirs("debug_faces", exist_ok=True)
                                 cv2.imwrite(f"debug_faces/face_{track_id}_{int(time.time())}.jpg", face_img)

                        label = f"ID:{track_id} {final_gender}"
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # --- C. Risk Analysis ---
            if not is_sos: # Only run detailed risk if not already Critical SOS
                risk_result = self.risk_engine.analyze(people_data, frame)
                
                # Logic: Send update if Risk is High/Moderate OR periodically for "Safe" heartbeat
                # This ensures the dashboard shows "Green" connectivity
                current_time = time.time()
                
                # Send immediately if Threat
                if risk_result['riskLevel'] in ['Moderate', 'Vulnerable']:
                     alert_data = {
                        "timestamp": current_time,
                        "riskLevel": risk_result['riskLevel'],
                        "riskScore": risk_result['riskScore'],
                        "description": risk_result['description'],
                        "location": LOCATION_NAME,
                        "latitude": LATITUDE,
                        "longitude": LONGITUDE
                    }
                     self.send_alert(alert_data)
                
                # Send "Safe" heartbeat every 2 seconds
                elif int(current_time) % 2 == 0:
                     # Simple throttling using modulo on epoch time (triggered once per second window roughly)
                     # A better way is tracking last_sent_time, but this is simple for demo
                     alert_data = {
                        "timestamp": current_time,
                        "riskLevel": "Safe",
                        "riskScore": risk_result.get('riskScore', 0),
                        "description": "System Active - Monitoring",
                        "location": LOCATION_NAME,
                        "latitude": LATITUDE,
                        "longitude": LONGITUDE
                    }
                     self.send_alert(alert_data)

                # Visuals
                # Color based on score (Green -> Yellow -> Red)
                score = risk_result.get('riskScore', 0)
                if score < 30: r_color = (0, 255, 0)
                elif score < 70: r_color = (0, 255, 255)
                else: r_color = (0, 0, 255)
                
                cv2.putText(frame, f"Risk: {risk_result['riskLevel']} ({score}%)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, r_color, 2)
                cv2.putText(frame, f"{risk_result['description']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)


            cv2.imshow("AI Engine - Eyes That Anticipate", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
        
        cap.release()
        cv2.destroyAllWindows()
        self.sio.disconnect()


if __name__ == '__main__':
    engine = AIEngine()
    engine.run()
