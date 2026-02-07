import numpy as np
import cv2
import time
from datetime import datetime

class RiskEngine:
    def __init__(self):
        self.risk_level = "Safe"
        self.risk_score = 0
        self.description = "Normal environment"
        
        # Tracking history for speed
        self.position_history = {} # ID -> [(x, y, time), ...]
        
        # Duration tracking (New)
        # pid -> {'start_time': timestamp, 'last_seen': timestamp, 'max_score': 0}
        self.duration_tracker = {} 
        
        # Constants & Weights (Total must sum to ~100 for max risk)
        self.W_PROXIMITY = 35    # Very close is dangerous
        self.W_ISOLATION = 15    # Alone is vulnerable
        self.W_MOTION = 20       # Running towards is aggressive
        self.W_TIME = 10         # Night time factor
        self.W_DURATION = 10     # Loitering factor
        self.W_CROWD = 10        # Surrounded factor

        # Thresholds
        self.PROXIMITY_THRESHOLD = 200 # Pixels (Start scoring)
        self.CRITICAL_PROXIMITY = 60   # Pixels (Max score)
        self.RUNNING_THRESHOLD_PIXELS = 15 
        self.LOITERING_TIME_THRESHOLD = 3.0 # Seconds before adding score

    def calculate_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def analyze(self, people_data, frame):
        """
        people_data: List of dicts {'box':..., 'centroid': (cx, cy), 'gender':..., 'id':...}
        """
        current_time = time.time()
        women = [p for p in people_data if p['gender'] == 'Female']
        men = [p for p in people_data if p['gender'] == 'Male' or p['gender'] == 'Unknown'] # Treat unknown as potential threat for safety
        
        # Default result if nobody is present
        if not people_data:
             return self._finalize_result(0, "No activity")

        # 1. Update Position History (Global)
        current_ids = set()
        for p in people_data:
            pid = p.get('id', -1)
            cx, cy = p['centroid']
            if pid != -1:
                current_ids.add(pid)
                if pid not in self.position_history:
                    self.position_history[pid] = []
                self.position_history[pid].append((cx, cy, current_time))
                if len(self.position_history[pid]) > 10: 
                    self.position_history[pid].pop(0)
        
        # Clean up stale IDs
        # (Optional: remove IDs from history if not seen for a while to save memory)

        # --- RISK CALCULATION ---
        # We calculate risk relative to the most vulnerable person (Woman)
        # If no women, risk is low unless fighting (future scope)
        
        if not women:
            return self._finalize_result(0, "Safe: No vulnerable subjects")

        max_risk_score = 0
        final_description = "Safe"

        for woman in women:
            w_score = 0
            w_desc_parts = []
            w_cx, w_cy = woman['centroid']
            
            # --- 1. TIME FACTOR (Global) ---
            current_hour = datetime.now().hour
            is_night = current_hour >= 20 or current_hour <= 6
            if is_night:
                w_score += self.W_TIME
                w_desc_parts.append("Night")

            # --- 2. ISOLATION / CROWD FACTOR ---
            # Alone?
            if len(people_data) == 1:
                w_score += self.W_ISOLATION
                w_desc_parts.append("Alone")
            
            # Surrounded by men?
            men_nearby_count = 0
            
            # --- 3, 4, 5. PROXIMITY, MOTION, DURATION (Per Man) ---
            max_man_threat = 0
            
            for man in men:
                m_pid = man.get('id', -1)
                m_cx, m_cy = man['centroid']
                dist = np.sqrt((w_cx - m_cx)**2 + (w_cy - m_cy)**2)
                
                man_score = 0
                
                # A. Proximity
                if dist < self.PROXIMITY_THRESHOLD:
                    men_nearby_count += 1
                    # Linear increase as distance decreases
                    # Score = Weight * (1 - dist/threshold)
                    factor = 1.0 - (dist / self.PROXIMITY_THRESHOLD)
                    man_score += self.W_PROXIMITY * factor

                    # B. Duration (Loitering)
                    if m_pid != -1:
                        if m_pid not in self.duration_tracker:
                            self.duration_tracker[m_pid] = {'start': current_time, 'last': current_time}
                        else:
                            self.duration_tracker[m_pid]['last'] = current_time
                            duration = current_time - self.duration_tracker[m_pid]['start']
                            if duration > self.LOITERING_TIME_THRESHOLD:
                                man_score += self.W_DURATION
                                if "Loitering" not in w_desc_parts: w_desc_parts.append("Loitering")

                # C. Motion (Running towards?)
                if m_pid != -1 and m_pid in self.position_history and len(self.position_history[m_pid]) >= 2:
                    prev_x, prev_y, prev_t = self.position_history[m_pid][-2]
                    curr_x, curr_y, curr_t = self.position_history[m_pid][-1]
                    
                    speed = np.sqrt((curr_x - prev_x)**2 + (curr_y - prev_y)**2)
                    
                    if speed > self.RUNNING_THRESHOLD_PIXELS:
                        # Check vector towards woman
                        dist_prev = np.sqrt((prev_x - w_cx)**2 + (prev_y - w_cy)**2)
                        if dist < dist_prev - 5: # Getting closer fast
                            man_score += self.W_MOTION
                            if "Approaching Fast" not in w_desc_parts: w_desc_parts.append("Approaching Fast")

                # Take the highest single threat vs cumulative? 
                # Let's add the threat of the most dangerous person
                max_man_threat = max(max_man_threat, man_score)

            w_score += max_man_threat
            
            # Additional crowd penalty if multiple men nearby
            if men_nearby_count >= 3:
                w_score += self.W_CROWD
                w_desc_parts.append(f"Surrounded ({men_nearby_count})")

            # Final Cap
            w_score = min(w_score, 100)
            
            if w_score > max_risk_score:
                max_risk_score = w_score
                final_description = ", ".join(w_desc_parts) if w_desc_parts else "Normal"

        return self._finalize_result(max_risk_score, final_description)

    def _finalize_result(self, score, description):
        # 0-30: Safe
        # 30-70: Moderate
        # 70+: Vulnerable
        if score < 30:
            level = "Safe"
        elif score < 70:
            level = "Moderate"
        else:
            level = "Vulnerable"
            
        return {
            "riskLevel": level,
            "riskScore": int(score),
            "description": description
        }
