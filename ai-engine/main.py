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


if __name__ == '__main__':
    engine = AIEngine()
    engine.run()
