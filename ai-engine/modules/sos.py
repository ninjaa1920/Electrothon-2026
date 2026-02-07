import cv2
import mediapipe as mp
import time
import os

class SOSDetector:
    def __init__(self):
        print("Initializing SOS Detector (Legacy MediaPipe)...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✅ SOS Detector Initialized (Legacy)")

    def detect(self, frame):
        """
        Detects SOS gesture (Open Palm) in the frame.
        Returns: True if SOS detected, else False
        """
        try:
            # Convert the image from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.hands.process(rgb_frame)
            
            is_sos = False
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    fingers = []
                    
                    # Landmarks:
                    # Thumb: 4
                    # Index: 8, Middle: 12, Ring: 16, Pinky: 20
                    # PIP/MCPs: -2 from tip
                    
                    # 1. Thumb (Tip 4 vs IP 3) - Simple check
                    # Check if thumb tip is "abducted" (far from palm center or just check x/y variance)
                    # For demo: easier to just counting 4 fingers (Index-Pinky) is enough for "Open Palm"
                    
                    # 2. Fingers (Index, Middle, Ring, Pinky)
                    # Check if TIP is ABOVE PIP (Y coordinate is smaller)
                    # Note: Y goes down.
                    
                    # Index (8 vs 6)
                    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y: fingers.append(1)
                    else: fingers.append(0)
                    
                    # Middle (12 vs 10)
                    if hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y: fingers.append(1)
                    else: fingers.append(0)

                    # Ring (16 vs 14)
                    if hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y: fingers.append(1)
                    else: fingers.append(0)
                    
                    # Pinky (20 vs 18)
                    if hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y: fingers.append(1)
                    else: fingers.append(0)

                    total_fingers = sum(fingers) # Max 4 from this loop
                    
                    # Also check thumb just in case (Tip 4 x vs Pinky Tip 20 x to see width?)
                    # Let's keep it simple: 4 fingers UP is an Open Palm SOS for this demo
                    
                    if total_fingers >= 4:
                        # print(f"DEBUG: Hand with {total_fingers} fingers up")
                        is_sos = True
                        break
            
            return is_sos, results.multi_hand_landmarks
            
        except Exception as e:
            print(f"SOS Detection Error: {e}")
            return False, None
