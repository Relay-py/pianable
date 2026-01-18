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
from instrument import Instrument
from draw_functions import SmokeParticle
import draw_functions


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
            hand_keypoints.append([thumb.x, thumb.y])
            hand_keypoints.append([index.x, index.y])
            hand_keypoints.append([middle.x, middle.y])
            hand_keypoints.append([ring.x, ring.y])
            hand_keypoints.append([pinky.x, pinky.y])

    return hand_keypoints


# constants for states
SELECT_PIANO = 0
SELECT_TABLE = 1
RUNNING = 2

def main():
    load_dotenv()

    # -------------- PYGAME THINGS --------------

    # initialize pygame
    pygame.init()

    # set up pygame
    pygame_screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    # array of corners clicked
    corner_positions = []
    # corners saved
    corners_saved = False
    # colour to indicate corner save status
    corner_colour = {True: "green", False: "red"}

    # keyboard points
    white_key_tops = []
    white_key_bases = []
    black_key_tops = []
    black_key_bases = []

    # array of table endpoints clicked
    endpoint_positions = []
    # endpoints saved
    endpoints_saved = False
    # colour to indicate endpoint save status
    endpoint_colour = {True: "green", False: "red"}

    # start pygame loop
    running = True

    # set current state in app
    state = SELECT_PIANO
    # -----------------------------------------

    # -------------- PROCESSING INIT --------------

    # Initialize mediapipe hand models
    hands_top, hands_front = initialize_mediapipe_hands(2)

    # Initialize the camera.
    top_cap = video.Video(1)
    front_cap = video.Video(0)

    # Initialize instruments
    instrument_top = InstrumentTop([], num_white_keys=7)
    instrument_front = InstrumentFront([], [], table_distance_threshold=0.02)

    soundfont_path = ""
    piano = Instrument(soundfont_path=soundfont_path)
    piano.start()


    # detect window height and width
    window_width, window_height = pygame.display.get_surface().get_size()

    total_time = 0
    total_frames = 0

    # list of particles that will appear when a key is played
    particles = []


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
                # Normalize clicked position
                clicked_position = np.array([event.pos[0] / window_width, event.pos[1] / window_height])

                # draw piano corner points
                if state == SELECT_PIANO:
                    # 4 corners not clicked yet -> add corner
                    if len(corner_positions) <= 3:
                        corner_positions.append(clicked_position)
                    # 4 corners clicked -> confirm
                    elif len(corner_positions) == 4:
                        state = SELECT_TABLE
                        # pass to calculator
                        instrument_top.set_corners(corner_positions)
                        # get back all key corners
                        white_key_tops, white_key_bases, black_key_tops, black_key_bases = instrument_top.get_all_keys_points()

                elif state == SELECT_TABLE:
                    # 2 endpoints not clicked yet -> add endpoint
                    if len(endpoint_positions) <= 1:
                        endpoint_positions.append(clicked_position)
                    # 2 endpoints clicked -> confirm
                    elif len(endpoint_positions) == 2:
                        # UPDATE INSTRUMENT_FRONT KEYPOINTS HERE
                        state = RUNNING
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
        if state == SELECT_PIANO and top_cap.isOpened():
            pygame_screen.fill((0, 0, 0))
            draw_functions.draw_frame(screen=pygame_screen, frame=top_frame)

            # draw points to indicate corners
            draw_functions.draw_points(screen=pygame_screen,
                        point_list=corner_positions,
                        colour=corner_colour[corners_saved])

        elif state == SELECT_TABLE and front_cap.isOpened():
            pygame_screen.fill((0, 0, 0))
            draw_functions.draw_frame(screen=pygame_screen, frame=front_frame)

            draw_functions.draw_points(screen=pygame_screen,
                        point_list=endpoint_positions,
                        colour=corner_colour[corners_saved])

        elif state == RUNNING and top_cap.isOpened() and front_cap.isOpened():
            pygame_screen.fill((0, 0, 0))

            # --------------- OPENCV LOOP ----------------

            # Process top camera
            if top_cap.isOpened():
                # Run processing for hand keypoints
                top_hand_keypoints = process_frame(top_frame, hands_top)

                # Draw hand points
                top_frame = draw_functions.draw_hand_points(top_frame, top_hand_keypoints)

                # convert and draw frame in pygame4
                new_width = window_width // 2
                new_height = window_height // 2
                draw_functions.draw_frame(screen=pygame_screen, frame=top_frame, 
                                          top_left=(0, 0), size=(new_width, new_height))
                # Draw white keys
                draw_functions.draw_keys(screen=pygame_screen, key_tops=white_key_tops, key_bases=white_key_bases, overlap=True,
                                         outline_colour="blue", outline_width=3, window_width=new_width, window_height=new_height)
                # Draw black keys
                draw_functions.draw_keys(screen=pygame_screen, key_tops=black_key_tops, key_bases=black_key_bases, overlap=False,
                                         outline_colour="red", outline_width=3, window_width=new_width, window_height=new_height)


            # Process front camera
            if front_cap.isOpened():
                front_frame = front_cap.read()

                if front_frame is None:
                    continue

                # Run processing for hand keypoints
                front_hand_keypoints = process_frame(front_frame, hands_front)

                # Draw hand points
                front_frame = draw_functions.draw_hand_points(front_frame, front_hand_keypoints)


                # convert and draw frame in pygame4
                new_width = window_width // 2
                new_height = window_height // 2
                draw_functions.draw_frame(screen=pygame_screen, frame=front_frame, 
                                          top_left=(0, new_height),
                                          size=(new_width, new_height))
                draw_functions.draw_tabletop(pygame_screen, endpoint_positions[0], endpoint_positions[1], "blue", 4, 
                                             top_left=(0, new_height), window_width=new_width, window_height=new_height)
                
            if top_cap.isOpened() and front_cap.isOpened() and len(top_hand_keypoints) > 0 and len(front_hand_keypoints) > 0:
            # if top_cap.isOpened() and front_cap.isOpened() and len(top_hand_keypoints) > 0:
                # Filter for pressed fingers
                pressed_fingers = instrument_front.get_pressed_fingers(front_hand_keypoints)

                # Get playing notes
                playing_notes = instrument_top.get_notes(pressed_fingers, white_key_tops, white_key_bases, black_key_tops, black_key_bases)

                print("Pressed fingers:", pressed_fingers)
                print("Corner positions", corner_positions)
                print("Playing notes!", playing_notes)
                print("----------------")


                #set up all the smoke for curent playing notes 
                for note_cordinate in playing_notes[1]:
                    for _ in range(30):
                        particles.append(SmokeParticle(note_cordinate[0], note_cordinate[1]))

            # Update all particles and remove dead ones
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            for p in particles:
                p.draw(pygame_screen)


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
    front_cap.release()
    cv2.destroyAllWindows()

    # uninit pygame or whatever
    pygame.quit()

    piano.stop()


if __name__ == "__main__":
    main()
