import numpy as np
from math_functions import in_quadrilateral , is_right_of_line , get_white_note

class InstrumentTop:
    def __init__(self,piano_corners,num_white_keys):
        self.piano_corners = piano_corners
        self.num_keys = num_white_keys
    
    def get_all_keys_points(self):
        '''
        [top left, top right, bottom left, bottom right]

        :param num_keys: Please provide the number of white keys only it should be divisible by 7 
                        for conviniency 
        
        :returns: 
            lines_top_point : the top point for each line beetween two keys 
            lines_bottom_point : the bottom point for each line beetween two keys
            black_keys_top_point :for each line beetween two keys the top two corners of the black key that
                                    is supposed to be there if no black key is there then the list contain a None
            black_keys_bottom_point : same as the previous one but for the bottom two points

             

        '''
        
        lines_top_point = [(self.piano_corners[1]-self.piano_corners[0])*i/self.num_keys +self.piano_corners[0] for i in range(self.num_keys+1)]
        lines_bottom_point = [(self.piano_corners[3]-self.piano_corners[2])*i/self.num_keys +self.piano_corners[2]  for i in range(self.num_keys+1)]
        black_keys_top_point =[]
        black_keys_bottom_point =[]

        for i in range(len(lines_top_point)):
            if i % 7 == 3 or i % 7 == 0:
                black_keys_top_point.append(None)
                black_keys_bottom_point.append(None)
                black_keys_top_point.append(None)
                black_keys_bottom_point.append(None)

            else: 
                value = ((lines_top_point[i] - lines_bottom_point[i]) * 3 / 10) + lines_bottom_point[i]
                previous = ((lines_top_point[i-1] - lines_bottom_point[i-1]) * 3 / 10) + lines_bottom_point[i-1]
                next  = ((lines_top_point[i+1] - lines_bottom_point[i-1]) * 3 / 10) + lines_bottom_point[i+1]

                first_top_corner =lines_top_point[i] -  (lines_top_point[i]-lines_top_point[i-1])/4 
                second_top_corner = (lines_top_point[i+1]-lines_top_point[i])/4 + lines_top_point[i]
                first_bottom_corner = value - (next - value)/4 
                second_botton_corner = (value -previous)/4 + value
                black_keys_top_point.append(first_top_corner)
                black_keys_bottom_point.append(first_bottom_corner)
                black_keys_top_point.append(second_top_corner)
                black_keys_bottom_point.append(second_botton_corner)

        return (lines_top_point, lines_bottom_point, black_keys_top_point, black_keys_bottom_point)
    
    def set_corners(self, corner_list):
        """
        sorts 4 corners into top left, top right, bottom left, bottom right
        and sets the attribute
        i do not like this algorithm but it is less typing so i'll take it

        :param corner_list: list of unordered corners
        """
        # 4 corners sorted by x coordinate
        corner_list.sort(key=(lambda a : a[0]))

        # 2 lower x coord corners (left) sorted by y
        left = corner_list[0:2]
        left.sort(key=(lambda a: a[1]))
        # 2 higher x coord corners (right) sorted by y
        right = corner_list[2:4]
        right.sort(key=(lambda a: a[1]))

        # native python list of corner positions
        sorted = [left[0], right[0], left[1], right[1]]
        # convert to numpy
        sorted_np = np.array(sorted,dtype=('int', 'int'))

        self.piano_corners = sorted_np
    

    def get_notes(self , fingers  , lines_top_point ,lines_bottom_point,black_keys_top_point , black_keys_bottom_point) :
        notes = []


        for finger in fingers:
            low = 0
            high = len(lines_bottom_point)-1
            while (low <= high) :
                mid = low + (high - low) // 2
                if in_quadrilateral(finger, lines_top_point[mid], lines_top_point[mid+1], lines_bottom_point[mid], lines_bottom_point[mid+1]) :
                    if in_quadrilateral(finger, black_keys_top_point[2*mid], black_keys_top_point[2*mid+1], black_keys_bottom_point[2*mid], black_keys_bottom_point[2*mid+1]):
                        notes.append(get_white_note(mid)-1)
                    
                    elif in_quadrilateral(finger, black_keys_top_point[2*mid+2], black_keys_top_point[2*mid+3], black_keys_bottom_point[2*mid+2], black_keys_bottom_point[2*mid+3]):
                        notes.append(get_white_note(mid)+1)

                    else:
                        notes.append(get_white_note(mid))
                    break
            
                if is_right_of_line(finger ,lines_top_point[mid],lines_bottom_point[mid] ) :
                    low = mid + 1

                else:
                    high = mid - 1

        return notes


        









if  __name__=="__main__":
    instrument = InstrumentTop(None,7)
    l1 = [0,0]
    l2 = [0,7]
    l3 = [7,0]
    l4 = [7,7]
    instrument.set_corners([l1,l2,l3,l4])
    a=instrument.get_all_keys_points()
    print(len(a[3]))
    fingers=([2.6,4],[2.3,3]) 
    b= instrument.get_notes(fingers, a[0], a[1], a[2], a[3])
    print(b)


    
    
    
   

