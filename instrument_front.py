import numpy as np
import cv2
from math_functions import distance_to_line


class InstrumentFront():
    def __init__(self, hand_keypoints, table_endpoints):
        self.hand_keypoints = hand_keypoints
        self.table_endpoints = table_endpoints


    def get_average_contour_y(self, contour):
        """Get the average y coordinate of the contour"""
        ys = contour[:, 0, 1]

        return float(np.mean(ys))
    

    def is_horizontal(self, contour, min_width=50, min_aspect_ratio=5):
        """Returns whether the given contour is horizontal"""
        _, _, width, height = cv2.boundingRect(contour)

        return width >= min_width and width / (height + 1e-5) >= min_aspect_ratio
    

    def calculate_contour_slope_and_intercept(self, contour):
        """"""
        # Squeeze and sort contour by increasing x coordinate
        contour = contour.squeeze()
        contour = sorted(contour, key=lambda p: p[0])

        x1, y1 = contour[0]
        x2, y2 = contour[-1]

        if x2 - x1 == 0:
            print(contour)
            raise ValueError("Contour is vertical line")
        
        slope = (y2 - y1) / (x2 - x1)
        y_intercept = y1 - slope * x1

        return slope, y_intercept
            

    def find_table(self, image):
        """INITIAL TABLE DETECTING ALGORITHM (DOESNT WORK) ;-;"""
        # 1. canny's the image
        # 2. detects contours
        # 3. filters the contours for long contours (eg > 50)
        # 4. determines the average y value of all remaining contours
        # 5. filters the remaining contours for those that are between y values 120 and 300
        # 6. filter those remaining contours for those that are horizontal
        # 7. calculates the interpolated line for those remaining contours
        # 8. finds the median slope and y intercept for those contours
        # 9. draws a line across the screen of that median slope and y intercept

        height, width, _ = image.shape

        colors = [
            (255, 0, 0),     # Blue
            (0, 255, 0),     # Green
            (0, 0, 255),     # Red
            (255, 255, 0),   # Cyan
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Yellow
            (255, 255, 255)  # White
        ]

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Canny edge detection
        edges = cv2.Canny(gray, 100, 150)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Copy image to draw on
        contour_img = image.copy()
        
        lower_y = 150
        upper_y = 250

        slopes = [0]
        y_intercepts = [200]
        drawn_contour = False
        i = 0
        for contour in contours:
            # Filter small contours
            if len(contour) < 50:
                continue

            average_y_value = self.get_average_contour_y(contour)

            if average_y_value < lower_y or average_y_value > upper_y:
                continue

            if not self.is_horizontal(contour):
                continue

            slope, y_intercept = self.calculate_contour_slope_and_intercept(contour)
            slopes.append(slope)
            y_intercepts.append(y_intercept)

            drawn_contour = True
            color = colors[i % len(colors)]
            cv2.drawContours(contour_img, [contour], -1, color, 2)
            i+=1

        if not drawn_contour:
            print("NOT DRAWN!!!!!")

        
        cv2.circle(contour_img, (100, lower_y), 3, (0, 0, 255), 3)
        cv2.circle(contour_img, (100, upper_y), 3, (0, 0, 255), 3)

        slopes.sort()
        y_intercepts.sort()

        if len(slopes) > 1 and len(y_intercepts) > 1:
            median_slope = slopes[len(slopes) // 2]
            median_y_intercept = y_intercepts[len(y_intercepts) // 2]
            print(slopes, median_slope, median_y_intercept)
            print("-------------------")
            cv2.line(contour_img,(0, int(median_y_intercept)),(width, int(median_slope * width + median_y_intercept)),(255,255,255),5)

        return edges


    def is_pressed(self, finger: list[float], threshold: int) -> bool:
        # Returns whether a given finger is close enough to the table line 
        # to be considered pressed
        # Pressing is determined by a threshold

        if self.keypoints is None:
            return False
                
        # Calculate distance to the table line
        dist = distance_to_line(finger, self.table_endpoints[0], self.table_endpoints[1])

        return dist <= threshold
    

    def set_endpoints(self, endpoint_list):
        """
        sorts 2 endpoints into left, right
        and sets the attribute

        :param corner_list: list of unordered corners
        """

        endpoint_list.sort(key=(lambda a : a[0]))

        self.table_endpoints = np.array(endpoint_list)


    