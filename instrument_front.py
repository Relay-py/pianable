import numpy as np
from math_functions import distance_to_line


class InstrumentFront():
    def __init__(self, hand_keypoints):
        self.hand_keypoints = hand_keypoints


    def is_pressed(self, finger: list[float], threshold: int) -> bool:
        # Returns whether a given finger is close enough to the table line 
        # to be considered pressed
        # Pressing is determined by a threshold

        if self.keypoints is None:
            return False
        
        top_right = self.keypoints[1]
        bottom_right = self.keypoints[2]
        
        # Calculate distance to the table line
        dist = distance_to_line(finger, top_right, bottom_right)

        return dist <= threshold


    