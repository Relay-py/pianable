import cv2
import mediapipe as mp
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np

# --- Configuration ---
MODEL_PATH = "model/runs/2026-01-18 06:09:55.323165/best.pt"  # Path to your trained .pt file
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps")
CROP_SIZE = 128
CONFIDENCE_THRESHOLD = 0.5

# Class mapping (Match this to your training labels!)
# 0 = Touching, 1 = Not Touching
CLASSES = {1: "Touching", 0: "No Touch"}
COLORS = {1: (0, 255, 0), 0: (0, 0, 255)} # Green for Touch, Red for No Touch

# MediaPipe Config
FINGER_INDICES = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky

def load_model(path):
    """
    Loads MobileNetV2 and adjusts the classifier head to match your training.
    """
    print(f"Loading model on {DEVICE}...")
    
    # 1. Initialize standard MobileNetV2
    model = models.mobilenet_v2(weights=None)
    
    # 2. Modify the classifier head to match your fine-tuning (2 output classes)
    # MobileNetV2 classifier structure:
    # (classifier): Sequential(
    #    (0): Dropout(p=0.2, inplace=False)
    #    (1): Linear(in_features=1280, out_features=1000, bias=True)
    # )
    model.classifier[1] = nn.Linear(model.last_channel, 2)
    
    # 3. Load weights
    try:
        model.load_state_dict(torch.load(path, map_location=DEVICE))
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Tip: Ensure the architecture here matches exactly how you saved it.")
        exit()
        
    model.to(DEVICE)
    model.eval() # Set to evaluation mode
    return model

def get_transforms():
    """
    Must match the validation transforms used during training.
    """
    return transforms.Compose([
        transforms.Resize((128, 128)), # Ensure size matches model expectation
        transforms.ToTensor(),
        # Standard ImageNet normalization (common for MobileNet)
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

def get_safe_crop(image, center_x, center_y, size):
    """
    Extracts crop with black padding if edges are reached.
    """
    h, w, _ = image.shape
    half_size = size // 2
    x1, y1 = center_x - half_size, center_y - half_size
    x2, y2 = x1 + size, y1 + size

    pad_top, pad_bottom = max(0, -y1), max(0, y2 - h)
    pad_left, pad_right = max(0, -x1), max(0, x2 - w)

    crop_x1, crop_y1 = max(0, x1), max(0, y1)
    crop_x2, crop_y2 = min(w, x2), min(h, y2)

    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]

    if pad_top > 0 or pad_bottom > 0 or pad_left > 0 or pad_right > 0:
        crop = cv2.copyMakeBorder(crop, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    return crop

def main():
    # 1. Setup
    model = load_model(MODEL_PATH)
    preprocess = get_transforms()
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(0) # 0 is usually the default webcam

    print("Starting inference loop... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb_frame)

        batch_tensors = []
        batch_coords = [] # Store (cx, cy) to draw on later

        # --- Data Collection Phase ---
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for idx in FINGER_INDICES:
                    lm = hand_landmarks.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    # Get Crop
                    crop = get_safe_crop(frame, cx, cy, CROP_SIZE)
                    
                    # Preprocess (Convert to PIL for torchvision transforms)
                    pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
                    input_tensor = preprocess(pil_img)
                    
                    batch_tensors.append(input_tensor)
                    batch_coords.append((cx, cy))

        # --- Inference Phase ---
        if batch_tensors:
            # Stack into a single batch: [N, 3, 128, 128]
            batch_stack = torch.stack(batch_tensors).to(DEVICE)
            
            with torch.no_grad():
                outputs = model(batch_stack)
                # Get predictions (Max logit)
                _, preds = torch.max(outputs, 1)
                
            # --- drawing Phase ---
            for i, prediction_idx in enumerate(preds):
                pred_class = prediction_idx.item() # 0 or 1
                cx, cy = batch_coords[i]
                
                # Choose color and text
                color = COLORS[pred_class]
                label = "T" if pred_class == 0 else "" # 'T' for touch, blank for none to reduce clutter
                
                # Draw visual indicator
                cv2.circle(frame, (cx, cy), 10, color, -1) # Filled circle
                cv2.circle(frame, (cx, cy), 12, (255, 255, 255), 1) # White border
                
                if label:
                    cv2.putText(frame, label, (cx - 5, cy - 15), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Show Result
        cv2.imshow('Hand Touch Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()