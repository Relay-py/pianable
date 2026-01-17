import pygame
import cv2


def draw_hand_points(frame, hand_keypoints):
    for point in hand_keypoints:
        x, y = int(point[0]), int(point[1])
        cv2.circle(frame, (x, y), 3, (0, 0, 255), 3)

    return frame


def draw_hand_points_pg(screen, hand_keypoints):
    """
    draw hand keypoints
    
    :param screen: pygame screen
    :param hand_keypoints: list of keybpoints
    """
    for point in hand_keypoints:
        pygame.draw.circle(surface=screen, color="red",
                           center=point, radius=2)


def draw_frame(screen, frame, x=0, y=0, width=None, height=None):
    """
    draws opencv frame on pygame screen

    :param screen: pygame screen
    :param frame: frame to draw (opencv brg matrix)
    :param start_point: top left corner formatted (x, y)
    """
    if width is not None and height is not None:
        frame = cv2.resize(frame, (width, height))

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (x, y))


def draw_points(screen, point_list, colour):
    """
    draw list of corners on given screen, with colour depending on whether they
    have been saved or not

    :param screen: pygame screen
    :param point_list: list of corner positions
    :param corners_saved: boolean
    """
    for corner in point_list:
        pygame.draw.circle(surface=screen,
                           color=colour,
                           center=corner,
                           radius=2)


def draw_keys(screen, key_tops, key_bases, overlap, outline_colour, outline_width):
    """
    draw polygons for white keys given coordinates
    the coordinates overlap

    :param screen: pygame screen
    :param key_tops: coordinates of key tops
    :param key_bases: coordinates of key bottoms
    :param overlap: boolean, true if 3 pairs of points for two keys, false if 4
    :param outline_colour: colour of key outline
    :param outline_colour: width of key outline
    """
    # don't draw anything if the lists of points are not the same length
    if len(key_tops) != len(key_bases):
        return None

    if overlap:
        step = 1
    else:
        step = 2

    for i in range(0, len(key_tops) - 1, step):
        # if no black key, don't draw
        if key_tops[i] is None:
            continue
        pygame.draw.polygon(surface=screen,
                            color=outline_colour,
                            points=(
                                key_tops[i],
                                key_tops[i+1],
                                key_bases[i+1],
                                key_bases[i]
                            ),
                            width=outline_width)


def draw_tabletop(screen, left, right, outline_colour, outline_width):
    """
    draw line for where table is being detected
    
    :param screen: pygame screen
    :param left: coordinate for left end
    :param right: coordinate for right end
    :param outline_colour: colour of key outline
    :param outline_colour: width of key outline
    """
    pygame.draw.line(surface=screen,
                     color=outline_colour,
                     start_pos=left,
                     end_pos=right,
                     width=outline_width)