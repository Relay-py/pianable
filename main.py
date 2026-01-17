import cv2
import os
import numpy as np
import mediapipe as mp
from dotenv import load_dotenv
import time
import video
import pygame
from instrument_top import InstrumentTop

from instrument_front import InstrumentFront


def initialize_mediapipe_hands(num_frames: int):
    # Initializes mediapipe hands models

    if num_frames > 2:
        raise ValueError("Maximum 2 frames permitted")

    mp_hands = mp.solutions.hands

    hands = []
    for _ in range(num_frames):
        hand = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        hands.append(hand)

    return hands


def process_frame(frame, hand_model):
    # Runs mediapipe hands on frame

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_results = hand_model.process(rgb_frame)
    height, width = frame.shape[:2]

    hand_keypoints = []
    if hand_results.multi_hand_landmarks:
        # Pick out the first and second hands
        for i in range(min(2, len(hand_results.multi_hand_landmarks))):
            hand_landmarks = hand_results.multi_hand_landmarks[i]

            # Define points for each finger
            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]
            middle = hand_landmarks.landmark[12]
            ring = hand_landmarks.landmark[16]
            pinky = hand_landmarks.landmark[20]

            # Unnormalize hand points
            hand_keypoints.append([thumb.x * width, thumb.y * height])
            hand_keypoints.append([index.x * width, index.y * height])
            hand_keypoints.append([middle.x * width, middle.y * height])
            hand_keypoints.append([ring.x * width, ring.y * height])
            hand_keypoints.append([pinky.x * width, pinky.y * height])

    return hand_keypoints


def draw_hand_points(frame, hand_keypoints):
    for point in hand_keypoints:
        x, y = int(point[0]), int(point[1])
        cv2.circle(frame, (x, y), 3, (0, 0, 255), 3)

    return frame


def draw_frame(screen, frame):
    """
    draws opencv frame on pygame screen

    :param screen: pygame screen
    :param frame: frame to draw (opencv brg matrix)
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))


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
        

def draw_white_keys(screen, key_tops, key_bases):
    """
    draw polygons for white keys given coordinates
    the coordinates overlap
    
    :param screen: pygame screen
    :param key_tops: coordinates of key tops
    :param key_bases: coordinates of key bottoms
    """
    # don't draw anything if the lists of points are not the same length
    if len(key_tops) != len(key_bases):
        return None
    
    for i in range(len(key_tops) - 1):
        pygame.draw.polygon(surface=screen,
                            color="azure",
                            points=(
                                key_tops[i],
                                key_tops[i+1],
                                key_bases[i],
                                key_bases[i+1]
                            ))


def main():
    load_dotenv()

    # -------------- PYGAME THINGS --------------

    # initialize pygame
    pygame.init()

    # set up pygame
    pygame_screen = pygame.display.set_mode((1280, 720))
    pygame_screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    # start pygame loop
    running = True

    # array of corners clicked
    corner_positions = []
    # corners saved
    corners_saved = False
    # colour to indicate corner save status
    corner_colour = {True: "green", False: "red"}

    # keyboard points
    instrument_top = InstrumentTop([], 14)
    instrument_front = InstrumentFront([], [])
    white_key_tops = []
    white_key_bases = []
    black_key_tops = []
    black_key_bases = []

    # -----------------------------------------
    # array of table endpoints clicked
    endpoint_positions = []
    # endpoints saved
    endpoints_saved = False
    # colour to indicate endpoint save status
    endpoint_colour = {True: "green", False: "red"}

    # 0 -> draw piano corners
    # 1 -> draw table endpoints
    # 2 -> running
    state = 0


    # -------------- PROCESSING INIT --------------

    # Initialize mediapipe hand models
    hands_top, hands_front = initialize_mediapipe_hands(2)


    # Initialize the camera. 
    top_cap = video.Video(0)
    front_cap =video.Video(1)


    #Set resolution
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    #cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    total_time = 0
    total_frames = 0

    # -------------------------------------------
    
    # --------------- EVENT LOOP ----------------
    while running:
        start = time.time()
        # poll for events
        for event in pygame.event.get():
            # check for exit (window close button)
            if event.type == pygame.QUIT:
                running = False
            # check for mouse left click
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                # draw piano corner points
                if state == 0:
                    # 4 corners not clicked yet -> add corner
                    if len(corner_positions) <= 3:
                        corner_positions.append(event.pos)
                    # 4 corners clicked -> confirm
                    elif len(corner_positions) == 4:
                        state = 1
                        # pass to calculator
                        instrument_top.set_corners(corner_positions)
                        # get back all key corners
                        white_key_tops, white_key_bases, black_key_tops, black_key_bases = instrument_top.get_all_keys_points()

                elif state == 1:
                    # 2 endpoints not clicked yet -> add endpoint
                    if len(endpoint_positions) <= 1:
                        endpoint_positions.append(event.pos)
                    # 2 endpoints clicked -> confirm
                    elif len(endpoint_positions) == 2:
                        # UPDATE INSTRUMENT_FRONT KEYPOINTS HERE
                        state = 2

                        instrument_front.set_endpoints(endpoint_positions)

        # Read top cap frame
        if top_cap.isOpened():
            top_frame = top_cap.read()

            if top_frame is None:
                continue

        # Read bottom cap frame
        if front_cap.isOpened():
            front_frame = front_cap.read()

            if front_frame is None:
                continue

        # Draw pygame frame for each state
        if state == 0 and top_cap.isOpened():
            draw_frame(screen=pygame_screen, frame=top_frame)

            # draw points to indicate corners
            draw_points(screen=pygame_screen,
                     point_list=corner_positions, 
                     colour=corner_colour[corners_saved])
            
        elif state == 1 and front_cap.isOpened():
            draw_frame(screen=pygame_screen, frame=front_frame)

            draw_points(screen=pygame_screen,
                     point_list=endpoint_positions, 
                     colour=corner_colour[corners_saved])

        elif state == 2 and top_cap.isOpened() and front_cap.isOpened():
            
        # --------------- OPENCV LOOP ----------------

            if top_cap.isOpened():
                # Run processing for hand keypoints
                top_hand_keypoints = process_frame(top_frame, hands_top)

                top_frame = draw_hand_points(top_frame, top_hand_keypoints)

                # cv2.imshow("Top Frame", top_frame)

                # convert and draw frame in pygame4
                draw_frame(screen=pygame_screen, frame=top_frame)

            # if front_cap.isOpened():
            #     front_frame = front_cap.read()

            #     if front_frame is None:
            #         continue

            #     # Run processing for hand keypoints
            #     front_hand_keypoints = process_frame(front_frame, hands_front)

            #     front_frame = draw_hand_points(front_frame, front_hand_keypoints)

            #     cv2.imshow("Front Frame", front_frame)
        
        # draw piano white keys
        print(white_key_tops)
        # draw_white_keys(screen=pygame_screen,
        #                 key_tops=white_key_tops,
        #                 key_bases=white_key_bases)

        # if not top_cap.isOpened() and not front_cap.isOpened():
        if not top_cap.isOpened():
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        end = time.time()
        if end - start < 1:
            total_time += end - start
            total_frames += 1

        # refresh pygame display????
        pygame.display.flip()
        clock.tick(60)

    average_time = 1000 * (total_time / total_frames)
    print("Average time per frame: ", average_time, "ms")
    print(1000 / average_time, "fps")

    top_cap.release()
    # front_cap.release()
    cv2.destroyAllWindows()

    # uninit pygame or whatever
    pygame.quit()


if __name__ == "__main__":
    main()
