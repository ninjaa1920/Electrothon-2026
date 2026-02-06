import cv2
import mediapipe as mp
import math

class SOSDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.5,
            max_num_hands=2
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        """
        Detects SOS gesture (Open Palm or Fist) in the frame.
        Returns: True if SOS detected, else False
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        sos_visual_data = [] # To draw on frame if needed

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Count extended fingers
                fingers = []
                
                # Thumb (Compare x-coordinates)
                # Note: Handedness check is better, but simple x-diff works for basic "is extended"
                # Assuming right hand logic for simplicity or checking relative to wrist
                if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                    fingers.append(1) # Extended
                else:
                    fingers.append(0)
                
                # Fingers 2-5 (Index to Pinky) - Compare y-coordinates
                for id in range(8, 21, 4):
                    if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                total_fingers = sum(fingers)
                
                # Logic: Open Palm (5 fingers) = STOP / HELP
                if total_fingers == 5:
                    return True, results.multi_hand_landmarks
                
                # Logic: Fist (0 fingers) = Distress (Optional)
                # if total_fingers == 0:
                #    return True, results.multi_hand_landmarks

        return False, None
