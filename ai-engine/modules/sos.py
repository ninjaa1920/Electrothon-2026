import cv2
import mediapipe as mp
import time
import os

# New MediaPipe Tasks API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class SOSDetector:
    def __init__(self, model_path='hand_landmarker.task'):
        print("Initializing SOS Detector (MediaPipe Tasks)...")
        
        if not os.path.exists(model_path):
            print(f"⚠️ Error: Model file '{model_path}' not found. Downloading...")
            # Fallback download if missing (though we did it manually)
            import urllib.request
            url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
            urllib.request.urlretrieve(url, model_path)
            print("Download complete.")

        # Create an HandLandmarker object.
        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(base_options=base_options,
                                                   num_hands=2)
            self.detector = vision.HandLandmarker.create_from_options(options)
            print("✅ SOS Detector Initialized Successfully")
        except Exception as e:
            print(f"❌ Failed to init SOS Detector: {e}")
            self.detector = None

    def detect(self, frame):
        """
        Detects SOS gesture (Open Palm or Fist) in the frame.
        Returns: True if SOS detected, else False
        """
        try:
            if self.detector is None: return False, None

            # Convert the image from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.array(rgb_frame, dtype=np.uint8) # FORCE UINT8 for mp
            
            # Create mp.Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect hand landmarks from the input image.
            detection_result = self.detector.detect(mp_image)
            
            is_sos = False
            
            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    fingers = []
                    
                    # Thumb: Ignore complex orientation logic for robust demo. 
                    # Just check if tip is far from pip (extended) based on distance
                    # thumb_tip = hand_landmarks[4]
                    # thumb_ip = hand_landmarks[3]
                    # if math.dist([thumb_tip.x, thumb_tip.y], [thumb_ip.x, thumb_ip.y]) > 0.05:
                    #     fingers.append(1)
                    
                    # Fingers 2-5 (Index to Pinky) - Vertical check (Y-axis) works best for "Stop" gesture
                    # Note: Y coordinates go DOWN in image space. So Tip < PIP means "Higher"
                    for id in range(8, 21, 4):
                        if hand_landmarks[id].y < hand_landmarks[id - 2].y:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    
                    total_fingers = sum(fingers)
                    
                    # Logic: Open Palm (>= 4 fingers up) = STOP / HELP / SOS
                    # This captures 4 fingers or 5 fingers (thumb often varies)
                    if total_fingers >= 4:
                        is_sos = True
                        break # Found one hand doing SOS is enough
            
            return is_sos, detection_result.hand_landmarks
            
        except Exception as e:
            # print(f"SOS Detection Error: {e}") # Silent fail to avoid spam
            return False, None
