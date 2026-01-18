import numpy as np


def distance(p1, p2):
    """Returns distance between two points"""

    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def distance_to_line(p, line_p1, line_p2):
    """Returns distance between a point p and a line defined by two points"""
    point_on_line = get_closest_point_to_line(p, line_p1, line_p2)

    return distance(p, point_on_line)


def get_closest_point_to_line(p, line_p1, line_p2):
    """Returns a point p' on the line (line_p1, line_p2) that is closest to point p"""
    projected_vector = get_projection_vector(p, line_p1, line_p2)

    return [line_p1[0] + projected_vector[0], line_p1[1] + projected_vector[1]]
    

def get_projection_vector(p, line_p1, line_p2):
    """Projects vector line_p1-p onto line_p1-line_p2
    args:
        p: list[int, int]
        line_p1: list[int, int]
        line_p2: list[int, int]
    
    returns: 
        projected vector: list[int, int]
    """

    line_vector = [line_p2[0] - line_p1[0], line_p2[1] - line_p1[1]]
    to_point_vector = [p[0] - line_p1[0], p[1] - line_p1[1]]

    line_vector_norm = np.linalg.norm(line_vector)
    if line_vector_norm == 0:
        raise Exception("Invalid line points")
    
    lhs = dot2d(line_vector, to_point_vector) / (line_vector_norm ** 2)

    return [lhs * line_vector[0], lhs * line_vector[1]]


def dot2d(p1, p2):
    return p1[0] * p2[0] + p1[1] * p2[1]
    

def in_quadrilateral(p, a, b, c, d):
    """Returns whether point p is in the quadrilateral defined by points
    (a, b, c, d)
    """
    if a is None : 
        return False

    def triangle_area(a, b, c):
        u = [b[0] - a[0], b[1] - a[1]]
        v = [c[0] - b[0], c[1] - b[1]]

        return 0.5 * abs(u[0] * v[1] - u[1] * v[0])
    
    quadrilateral_area = triangle_area(a, b, c) + triangle_area(b, d, c)
    point_triangle_sum = triangle_area(a, b, p) + triangle_area(a, p, c) + triangle_area(c, p, d) + triangle_area(d, p, b)
    # print(quadrilateral_area,point_triangle_sum)
    return abs(quadrilateral_area - point_triangle_sum) < 0.001



def is_right_of_line(p, a, b):
    '''checks if point p is in the right of the line between a and b '''
    if (b[0] - a[0]) < 0.001 :
        return  a[0] < p[0] 
    slope  = (  b[1]-a[1] )/ (b[0] - a[0] )
    basis  = a[1] - slope*a[0]
    if slope > 0 :
        return p[1]- (slope * p[0] +basis) < 0
    else :
        return p[1]- (slope * p[0] +basis) > 0
    
def get_white_note(index):
    return 5*(index//7) +index + index%7 -1 *(index%7 > 2)


    

if __name__ == "__main__":
    print(in_quadrilateral([2.6,4] , [0,0], [7,0] , [0,7] , [7,7]))

