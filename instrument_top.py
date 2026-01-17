import numpy as np


class InstrumentTop():
    def __init__(self,piano_corners,num_white_keys):
        self.piano_corners = piano_corners
        self.num_keys = num_white_keys
    
    def get_all_keys(self, num_keys):
        
        lines_bottom_point = [(self.piano_corners[0]-self.piano_corners[1])*i+self.piano_corners[0] for i in range(num_keys+1)]
        lines_top_point = [(self.piano_corners[2]-self.piano_corners[3])*i+self.piano_corners[2]   for i in range(num_keys+1)]
        lines_top_point_draw = [
            None if i % 3 == 0 or i % 7 == 0
            else ((lines_top_point[i] - lines_bottom_point[i]) * 3 / 5) + lines_bottom_point[i]
            for i in range(len(lines_top_point))
        ]

        
        return (lines_top_point , lines_bottom_point)
    
   

