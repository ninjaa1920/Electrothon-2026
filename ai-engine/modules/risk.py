import numpy as np
import cv2
from datetime import datetime

class RiskEngine:
    def __init__(self):
        self.risk_level = "Low"
        self.description = "Normal"
        
        # Thresholds
        self.PROXIMITY_THRESHOLD = 150 # Pixels (Adjust based on camera resolution)
        self.SURROUNDING_COUNT_THRESHOLD = 3
        
    def calculate_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def analyze(self, people_data, frame):
        """
        people_data: List of dicts {'box': [x1,y1,x2,y2], 'centroid': (cx, cy), 'gender': 'Male'/'Female'}
        frame: The current video frame (for pixel difference check if needed)
        """
        self.risk_level = "Low"
        self.description = "Normal environment"
        
        women = [p for p in people_data if p['gender'] == 'Female']
        men = [p for p in people_data if p['gender'] == 'Male']
        
        # Scenario 1: Lone Woman at Night
        current_hour = datetime.now().hour
        is_night = current_hour >= 20 or current_hour <= 6
        
        if len(women) == 1 and len(people_data) == 1 and is_night:
            # Check Pixel Density/Motion around her (Mocked for now, implementing simplified version)
            # If we had previous frame we could check motion
            self.risk_level = "High"
            self.description = "Lone woman detected at night"
            return self.get_result()

        # Scenario 2: Woman Surrounded (Proximity Logic)
        # "convert coordinates into risk levels....like coordinates ki distance subtract krke detect Krle risk"
        for woman in women:
            close_men_count = 0
            w_cx, w_cy = woman['centroid']
            
            for man in men:
                m_cx, m_cy = man['centroid']
                # Coordinate subtraction / Euclidean distance
                distance = np.sqrt((w_cx - m_cx)**2 + (w_cy - m_cy)**2)
                
                if distance < self.PROXIMITY_THRESHOLD:
                    close_men_count += 1
            
            if close_men_count >= self.SURROUNDING_COUNT_THRESHOLD:
                self.risk_level = "Critical"
                self.description = f"Woman surrounded by {close_men_count} men nearby"
                return self.get_result()
                
            if close_men_count > 0 and is_night:
                 self.risk_level = "High"
                 self.description = "Woman accompanied by men at night"
        
        return self.get_result()

    def get_result(self):
        return {
            "riskLevel": self.risk_level,
            "description": self.description
        }
