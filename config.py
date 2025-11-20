"""
Project Configuration Module.
Centralizes all static parameters, paths, and calibration thresholds
to ensure easy tuning without modifying core logic.
"""

## === [ PATHS & I/O ] ===
# Path to the trained YOLO weights
MODEL_PATH = "runs/detect/CocoDetec/weights/best.pt"

# Input video file path or Camera ID (0 for webcam)
VIDEO_SOURCE = "test_vid/Coconut Counter _ Camera-based Coconuts Counting for Conveyor Belts with Machine Vision & AI.mp4"

## === [ COUNTING LINE CONFIGURATION ] ===
# Vertical position of the counting line (0.0 = Top, 1.0 = Bottom)
LINE_POSITION = 0.5

# Hysteresis buffer zone in pixels (prevents double counting on line jitter)
OFFSET_PX = 20

## === [ QUALITY CONTROL (QC) CALIBRATION ] ===
# Pixel area thresholds for size classification
# Adjust these values based on camera distance and resolution
SIZE_THRESHOLDS = {
    'small_limit': 20000,   # Below this is 'Small'
    'medium_limit': 30000   # Below this is 'Medium', above is 'Large'
}

# Minimum average V-channel brightness (0-255) to be considered 'Good'
# Lower values indicate dark/rotten coconuts or shadows
QUALITY_BRIGHTNESS_THRESH = 127 

# Crack detection sensitivity (0.0 to 1.0)
# Represents the ratio of dark fissure pixels to total coconut area.
# 0.2 means if 20% of the surface has dark lines, it is flagged as cracked.
CRACK_LIMIT_RATIO = 0.2 

## === [ MODEL TRAINING HYPERPARAMETERS ] ===
# Configuration passed directly to the YOLOv11 train() method
TRAIN_CONFIG = {
    'epochs': 100,
    'patience': 50,
    'batch': 32,
    'imgsz': 640,
    'project': 'runs/detect',
    'name': 'Coconut_Detec', 
    
    # Augmentation Hyperparameters
    'degrees': 25.0,        
    'scale': 0.6,           
    'shear': 2.0,           
    'translate': 0.1,       
    'fliplr': 0.5,          
    'flipud': 0.5,          
    'mosaic': 1.0,          
    'mixup': 0.4,           
    'copy_paste': 0.1       
}