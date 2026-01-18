import pygame
import cv2
from SoundButton2 import SoundButton
import numpy as np


def unnormalize_point(screen, point, width=None, height=None):
    if not width and not height:
        width, height = screen.get_size()

    return (int(point[0] * width), int(point[1] * height))


def draw_hand_points(frame, hand_keypoints):
    # Unnormalize points
    h, w, _ = frame.shape

    for point in hand_keypoints:
        x, y = int(point[0] * w), int(point[1] * h)
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


def draw_frame(screen, frame, top_left=np.array((0, 0)), size=None):
    """
    draws opencv frame on pygame screen

    :param screen: pygame screen
    :param frame: frame to draw (opencv brg matrix)
    :param top_left: top left corner formatted (x, y)
    :param size: (width, height) to draw it at
    """
    # get frame info (height and width are supposed! to be switched this is correct)
    frame_size = [frame.shape[1], frame.shape[0]]
    
    # get size of target area to display on (default is entire screen)
    if size is None:
        target_size = screen.get_size()
    else:
        target_size = size

    # find scaled size depending which aspect is bigger compared to target
    scale_factor = min(target_size[0]/frame_size[0], target_size[1]/frame_size[1])
    new_frame_size = [int(frame_size[0] * scale_factor), int(frame_size[1] * scale_factor)]

    # resize if needed
    if new_frame_size != frame_size:
        frame = cv2.resize(frame, new_frame_size)

    # draw frame
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, top_left)


def draw_points(screen, point_list, colour):
    """
    draw list of corners on given screen, with colour depending on whether they
    have been saved or not

    :param screen: pygame screen
    :param point_list: list of corner positions
    :param corners_saved: boolean
    """
    for corner in point_list:
        # Unnormalize points
        corner = unnormalize_point(screen, corner)

        pygame.draw.circle(surface=screen,
                           color=colour,
                           center=corner,
                           radius=2)


def draw_keys(screen, key_tops, key_bases, overlap, outline_colour, outline_width,
              top_left=np.array((0, 0)), scale_factor = 1, window_width=None, window_height=None):
    """
    draw polygons for white keys given coordinates
    the coordinates overlap

    :param screen: pygame screen
    :param key_tops: coordinates of key tops
    :param key_bases: coordinates of key bottoms
    :param overlap: boolean, true if 3 pairs of points for two keys, false if 4
    :param outline_colour: colour of key outline
    :param outline_colour: width of key outline
    :param top_left: top left of the frame that it should be drawn above
    :param scale_factor: whether to resize or not
    """
    # don't draw anything if the lists of points are not the same length
    if len(key_tops) != len(key_bases):
        return None
    
    # Unnormalize key tops and bases
    if window_width is not None and window_height is not None:
        key_tops = np.array([
            [p[0] * window_width, p[1] * window_height] if p is not None else None
            for p in key_tops
        ], dtype=object)

        key_bases = np.array([
            [p[0] * window_width, p[1] * window_height] if p is not None else None
            for p in key_bases
        ], dtype=object)


    if overlap:
        step = 1
    else:
        step = 2


    for i in range(0, len(key_tops) - 1, step):
        # if no black key, don't draw
        if key_tops[i] is None:
            continue

        # new_key_tops = key_tops * scale_factor + top_left
        # new_key_bases = key_bases * scale_factor + top_left
        new_key_top1 = key_tops[i] * scale_factor + top_left
        new_key_top2 = key_tops[i+1] * scale_factor + top_left
        new_key_base1 = key_bases[i] * scale_factor + top_left
        new_key_base2 = key_bases[i+1] * scale_factor + top_left

        pygame.draw.polygon(surface=screen,
                            color=outline_colour,
                            points=(
                                new_key_top1,
                                new_key_top2,
                                new_key_base2,
                                new_key_base1,
                            ),
                            width=outline_width)


def draw_tabletop(screen, left, right, outline_colour, outline_width,
                  top_left=np.array((0, 0)), window_width=None, window_height=None):
    """
    draw line for where table is being detected
    
    :param screen: pygame screen
    :param left: coordinate for left end
    :param right: coordinate for right end
    :param outline_colour: colour of key outline
    :param outline_colour: width of key outline
    :param top_left: top left of the frame that it should be drawn above
    """
    left = list(np.array(unnormalize_point(screen, left, window_width, window_height)) + top_left)
    right = list(np.array(unnormalize_point(screen, right, window_width, window_height)) + top_left)

    pygame.draw.line(surface=screen,
                     color=outline_colour,
                     start_pos=left,
                     end_pos=right,
                     width=outline_width)
    

def draw_soundbuttons(screen, buttons, mouse_position, current_sound):
    """
    draw buttons

    :param screen: pygame screen
    :param buttons: list of SoundButton objects
    """
    for button in buttons:
        if button.collides(mouse_position) or current_sound == button.sound:
            # mouse is on top of button
            pygame.draw.rect(surface=screen, color=button.colour, rect=button.rect,
                            border_radius=15)
            screen.blit(button.hovertext, button.hovertext.get_rect(center=button.rect.center))
        else:
            # mouse is not hovering
            pygame.draw.rect(surface=screen, color=button.colour, rect=button.rect, width=4,
                            border_radius=15)
            screen.blit(button.text, button.text.get_rect(center=button.rect.center))
