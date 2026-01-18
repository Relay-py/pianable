import cv2
import os
import numpy as np
import mediapipe as mp
from dotenv import load_dotenv
import time
import video
import pygame
import fluidsynth
from instrument_top import InstrumentTop
from instrument_front import InstrumentFront
from instrument import Instrument
from NoteRise import RisingNote, Spark
import draw_functions
import random
from log import log
from SoundButton2 import SoundButton  , draw_gradient_background

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

    left_hand_keypoints = []
    right_hand_keypoints = []

    if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
        for landmarks, handedness in zip(
            hand_results.multi_hand_landmarks,
            hand_results.multi_handedness
        ):
            # get handedness label ("Left" or "Right")
            label = handedness.classification[0].label

            # fingertip indices
            finger_indices = [4, 8, 12, 16, 20]

            points = [
                [landmarks.landmark[i].x, landmarks.landmark[i].y]
                for i in finger_indices
            ]

            if label == "Left":
                left_hand_keypoints = points
            elif label == "Right":
                right_hand_keypoints = points

    return left_hand_keypoints, right_hand_keypoints


def play_notes(piano: Instrument, playing_notes) -> None:
    """Plays notes on instrument
    args:
        piano: Intrument
        playing_notes: set of playing notes

    returns:
        None
    """

    for i in range(50, 140):
        if piano.is_playing(i):
            if i not in playing_notes:
                piano.remove_note(i)
        else:
            if i in playing_notes:
                piano.add_note(i)


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
    top_cap = video.Video(0)
    front_cap = video.Video(2)

    # Initialize instruments
    instrument_top = InstrumentTop([], num_white_keys=7)
    instrument_front = InstrumentFront([], [], table_distance_threshold=0.015)

    # soundfont_path = "Soundfont.sf2"
    # piano = Instrument(soundfont_path=soundfont_path, preset=0, volume=100)
    # piano.start()


    # detect window height and width
    window_width, window_height = pygame.display.get_surface().get_size()

    total_time = 0
    total_frames = 0

    # list of particles that will appear when a key is played
    particles = []
    active_rising_notes = {}
    finished_notes = []

    # -------------------------------------------


    # ------------- INIT SOUNDS ------------------
    piano = Instrument(os.path.join(".", "Soundfont.sf2"), 0, 0, 50)
    all_soundbuttons = piano.generate_soundbuttons(group_top_left=(window_width // 2 + 100, 50),
                                                  size=(150, 50),
                                                  padding=(25, 10))

    piano.start()

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
                clicked_position = np.array(
                    [event.pos[0] / window_width, event.pos[1] / window_height])

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

                elif state == RUNNING:
                    # check whether any of the sound buttons are clicked
                    for button in all_soundbuttons:
                        if button.collides(event.pos):
                            piano.change_sound(button.sound)


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
            draw_gradient_background(pygame_screen, window_width, window_height)

            # --------------- OPENCV LOOP ----------------

            # Process top camera
            if top_cap.isOpened():
                # Run processing for hand keypoints
                top_hand_keypoints_left, top_hand_keypoints_right = process_frame(top_frame, hands_top)
                
                # Draw hand points
                top_frame = draw_functions.draw_hand_points(top_frame, top_hand_keypoints_left)
                top_frame = draw_functions.draw_hand_points(top_frame, top_hand_keypoints_right)

                # convert and draw frame in pygame4
                new_width = window_width // 2
                new_height = window_height // 2
                draw_functions.draw_frame(screen=pygame_screen, frame=top_frame,
                                          size=(new_width, new_height))
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
                front_hand_keypoints_left, front_hand_keypoints_right = process_frame(front_frame, hands_front)

                # Draw hand points
                front_frame = draw_functions.draw_hand_points(front_frame, front_hand_keypoints_left)
                front_frame = draw_functions.draw_hand_points(front_frame, front_hand_keypoints_right)


                # convert and draw frame in pygame4
                new_width = window_width // 2
                new_height = window_height // 2
                draw_functions.draw_frame(screen=pygame_screen, frame=front_frame, 
                                          top_left=np.array((0, new_height)),
                                          size=(new_width, new_height))
                draw_functions.draw_tabletop(pygame_screen, endpoint_positions[0], endpoint_positions[1], "blue", 4, 
                                             top_left=np.array((0, new_height)), window_width=new_width, window_height=new_height)

                
            mouse_p = pygame.mouse.get_pos()
            cur_s = (piano.bank, piano.preset)
            for button in all_soundbuttons:
                button.draw(pygame_screen, mouse_p, cur_s)
                
            if top_cap.isOpened() and front_cap.isOpened() and len(top_hand_keypoints_left) > 0 and len(front_hand_keypoints_left) > 0:
            # if top_cap.isOpened() and front_cap.isOpened() and len(front_hand_keypoints) > 0:
                # Filter for pressed fingers
                pressed_fingers_left = instrument_front.get_pressed_fingers(front_hand_keypoints_left, top_hand_keypoints_left)
                pressed_fingers_right = instrument_front.get_pressed_fingers(front_hand_keypoints_right, top_hand_keypoints_right)
                pressed_fingers = pressed_fingers_left + pressed_fingers_right

                # Get playing notes
                playing_notes = instrument_top.get_notes(
                    pressed_fingers, white_key_tops, white_key_bases, black_key_tops, black_key_bases)
                playing_midi_notes = {instrument_top.index_to_midi(
                    note) for note in playing_notes[0]}

                print("Pressed fingers:", pressed_fingers)
                print("Corner positions", corner_positions)
                print("Playing notes!", playing_midi_notes)
                print("----------------")

                play_notes(piano, playing_midi_notes)
                # set up all the smoke for curent playing notes
                for note_idx, coord, width, x_coord in zip(playing_notes[0], playing_notes[1], playing_notes[2], playing_notes[3]):
                    midi_id = instrument_top.index_to_midi(note_idx)
                    # Use coordinate relative to top-left camera view
                    px_x = coord[0] * window_width // 2
                    px_y = coord[1] * window_height // 2
                    px_w = width * window_width // 2
                    px_x_top_left = x_coord * window_width // 2

                    if midi_id not in active_rising_notes:

                        color = random.choice(
                            [(0, 255, 150), (0, 220, 255), (255, 100, 255), (255, 255, 100)])
                        active_rising_notes[midi_id] = RisingNote(
                            px_x_top_left, px_y, px_w, color)

                    # Add sparkles at the key point every frame the finger is down
                    for _ in range(3):
                        particles.append(
                            Spark(px_x, px_y, active_rising_notes[midi_id].color))

                # 2. Transition notes to "Finished" once finger is lifted
                for m_id in list(active_rising_notes.keys()):
                    if m_id not in playing_midi_notes:
                        note_obj = active_rising_notes.pop(m_id)
                        note_obj.is_active = False
                        finished_notes.append(note_obj)

            else:
                piano.remove_all_notes()
                for m_id, note_obj in active_rising_notes.items():
                    note_obj.is_active = False
                    finished_notes.append(note_obj)
                active_rising_notes.clear()

            # Update all particles and remove dead ones
            for p in particles[:]:
                p.update()
                p.draw(pygame_screen)
                if p.life <= 0:
                    particles.remove(p)

            # Draw Notes
            all_visible_notes = finished_notes + \
                list(active_rising_notes.values())
            for note in all_visible_notes[:]:
                note.update()
                note.draw(pygame_screen)
                # Cleanup notes that flew off the top
                if note.y + note.h < -100:
                    if note in finished_notes:
                        finished_notes.remove(note)

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




