import cv2
import mediapipe as mp
import os
import sys
import shutil  # Added for moving files

# --- Configuration ---
INPUT_DIR = "model/unlabeled_images"
COMPLETED_DIR = "model/labeled_images"  # <--- New directory for finished source images

DIRS = {
    ord('0'): "not-touching",  # Key '0'
    ord('1'): "touching",      # Key '1'
    ord(' '): "skipped_images" # Spacebar
}

CROP_SIZE = 128     
DISPLAY_SIZE = 512  
FINGER_INDICES = [4, 8, 12, 16, 20] 
FINGER_NAMES = {4: 'Thumb', 8: 'Index', 12: 'Middle', 16: 'Ring', 20: 'Pinky'}

def setup_directories():
    """Creates output directories if they don't exist."""
    for folder in DIRS.values():
        os.makedirs(folder, exist_ok=True)
    
    # Create the directory for finished source images
    os.makedirs(COMPLETED_DIR, exist_ok=True)
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Directory '{INPUT_DIR}' not found. Please create it and add images.")
        sys.exit()

def get_safe_crop(image, center_x, center_y, size):
    """
    Crops the image around center_x, center_y with padding for edges.
    """
    h, w, _ = image.shape
    half_size = size // 2

    x1 = center_x - half_size
    y1 = center_y - half_size
    x2 = x1 + size
    y2 = y1 + size

    pad_top = max(0, -y1)
    pad_bottom = max(0, y2 - h)
    pad_left = max(0, -x1)
    pad_right = max(0, x2 - w)

    crop_x1 = max(0, x1)
    crop_y1 = max(0, y1)
    crop_x2 = min(w, x2)
    crop_y2 = min(h, y2)

    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]

    if pad_top > 0 or pad_bottom > 0 or pad_left > 0 or pad_right > 0:
        crop = cv2.copyMakeBorder(crop, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return crop

def create_visualization(frame, crop, cx, cy, finger_name, hand_idx):
    """
    Creates a side-by-side view: Context (Left) + Zoomed Crop (Right)
    """
    zoomed_view = cv2.resize(crop, (DISPLAY_SIZE, DISPLAY_SIZE), interpolation=cv2.INTER_NEAREST)
    
    context_view = frame.copy()
    box_half = CROP_SIZE // 2
    cv2.rectangle(context_view, 
                  (cx - box_half, cy - box_half), 
                  (cx + box_half, cy + box_half), 
                  (0, 255, 0), 2)
    
    h, w, _ = context_view.shape
    scale_factor = DISPLAY_SIZE / h
    new_w = int(w * scale_factor)
    context_view = cv2.resize(context_view, (new_w, DISPLAY_SIZE))
    
    combined = cv2.hconcat([context_view, zoomed_view])
    
    cv2.putText(combined, f"{finger_name} (Hand {hand_idx})", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(combined, "<- Context | Zoom ->", (new_w - 80, DISPLAY_SIZE - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    
    return combined

def main():
    setup_directories()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5
    )

    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(image_files)} images.")
    print("Controls: '0' = Touching | '1' = Not-Touching | 'Space' = Skip | 'Esc' = Quit")

    for filename in image_files:
        filepath = os.path.join(INPUT_DIR, filename)
        frame = cv2.imread(filepath)
        
        if frame is None:
            print(f"Could not read {filename}, skipping.")
            continue

        height, width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            print(f"No hands found in {filename}. Moving to skipped.")
            # Optional: Move to skipped if no hands found, or just leave it.
            # For now, let's leave it in unlabeled or move it to a "no_hands" folder if you prefer.
            continue

        # --- Labeling Loop ---
        quit_program = False
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            for finger_idx in FINGER_INDICES:
                lm = hand_landmarks.landmark[finger_idx]
                
                cx, cy = int(lm.x * width), int(lm.y * height)
                crop = get_safe_crop(frame, cx, cy, CROP_SIZE)

                finger_name = FINGER_NAMES.get(finger_idx, "Unknown")
                display_img = create_visualization(frame, crop, cx, cy, finger_name, hand_idx)

                cv2.imshow("Label Data", display_img)
                
                valid_key = False
                while not valid_key:
                    key = cv2.waitKey(0)

                    if key == 27: # ESC
                        quit_program = True
                        valid_key = True
                        break
                    
                    if key in DIRS:
                        target_dir = DIRS[key]
                        base_name = os.path.splitext(filename)[0]
                        save_name = f"{base_name}_h{hand_idx}_f{finger_idx}.jpg"
                        save_path = os.path.join(target_dir, save_name)
                        
                        cv2.imwrite(save_path, crop)
                        print(f"Saved: {save_name} -> {target_dir}")
                        valid_key = True
            
            if quit_program:
                break
        
        if quit_program:
            print("Exiting...")
            break

        # --- Move Original Image ---
        # If we reached this point, we finished the loop for this image (didn't quit)
        try:
            destination = os.path.join(COMPLETED_DIR, filename)
            shutil.move(filepath, destination)
            print(f"Moved source image to: {COMPLETED_DIR}")
        except Exception as e:
            print(f"Error moving file: {e}")

    print("Done.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()