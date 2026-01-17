import numpy as np
from math_functions import in_quadrilateral

class InstrumentTop():
    def __init__(self,piano_corners,num_white_keys):
        self.piano_corners = piano_corners
        self.num_keys = num_white_keys
    
    def get_all_keys_points(self):
        '''
        Docstring for get_all_keys

        :param
             num_keys: Please provide the number of white keys only it should be divisible by 7 
                        for conviniency 
        
        :returns 
            lines_top_point : the top point for each line beetween two keys 
            lines_bottom_point : the bottom point for each line beetween two keys
            black_keys_top_point :for each line beetween two keys the top two corners of the black key that
                                    is supposed to be there if no black key is there then the list contain a None
            black_keys_bottom_point : same as the previous one but for the bottom two points

             

        '''

        
        lines_top_point = [(self.piano_corners[1]-self.piano_corners[0])*i+self.piano_corners[0] for i in range(self.num_keys+1)]
        lines_bottom_point = [(self.piano_corners[3]-self.piano_corners[2])*i+self.piano_corners[2]  for i in range(self.num_keys+1)]
        lines_top_point_draw =[]
        black_keys_top_point =[]
        black_keys_bottom_point =[]

        for i in range(len(lines_top_point)):
            if i % 3 == 0 or i % 7 == 0:
                lines_top_point_draw.append(lines_top_point[i])
                black_keys_top_point.append(None)
                black_keys_bottom_point.append(None)
                black_keys_top_point.append(None)
                black_keys_bottom_point.append(None)

            else: 
                value = ((lines_top_point[i] - lines_bottom_point[i]) * 3 / 5) + lines_bottom_point[i]
                previous = ((lines_top_point[i-1] - lines_bottom_point[i-1]) * 3 / 5) + lines_bottom_point[i-1]
                next  = ((lines_top_point[i+1] - lines_bottom_point[i-1]) * 3 / 5) + lines_bottom_point[i+1]

                lines_top_point_draw.append(((lines_top_point[i] - lines_bottom_point[i]) * 3 / 5) + lines_bottom_point[i])

                first_top_corner = (lines_top_point[i]-lines_top_point[i-1])/4 + lines_top_point[i-1]
                second_top_corner = (lines_top_point[i+1]-lines_top_point[i])/4 + lines_top_point[i]
                first_bottom_corner = (value -previous)/4 + previous
                second_botton_corner = (next - value)/4 + value
                black_keys_top_point.append(first_top_corner)
                black_keys_bottom_point.append(first_bottom_corner)
                black_keys_top_point.append(second_top_corner)
                black_keys_bottom_point.append(second_botton_corner)

        return (lines_top_point ,lines_bottom_point,black_keys_top_point , black_keys_bottom_point)
    

    # def get_notes(self , fingers  , lines_top_point ,lines_bottom_point,black_keys_top_point , black_keys_bottom_point) :
    #     notes = []


    #     for finger in fingers:
    #         low = 0
    #         high = len(lines_bottom_point)-1
    #         while (low <= high) :
    #             mid = low + (high - low) / 2
    #             if in_quadrilateral(finger ,lines_top_point[mid] ,lines_top_point[mid+1] , lines_bottom_point[mid] ,lines_bottom_point[mid+1]) :
    #                 if in_quadrilateral(finger ,black_keys_top_point[2*mid] ,black_keys_top_point[2*mid+1] , black_keys_bottom_point[2*mid] ,black_keys_bottom_point[2*mid+1]):
    #                     notes.append(mid , 'black' )
    #                 else:
    #                     notes.append(mid , 'black' )
    #                 break
            
    #             if is_right_quadrelateral() :

    #                 low = mid + 1

    #             else
    #                 high = mid - 1










    
   

