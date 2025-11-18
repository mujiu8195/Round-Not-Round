import cv2
import numpy as np
import os
import time

SAVE_FOLDER = r"H:\person\p"
LIGHT_THRESHOLD = 200  
BRIGHT_AREA_THRESHOLD = 0.10 
STABILITY_FRAMES = 10  # Changed to 10 frames for stable dark detection
COOLDOWN_TIME = 2.0  
CAMERA_INDEX = 0 
HORIZONTAL_RESOLUTION = (1024, 768) 
VERTICAL_RESOLUTION = (768, 1024)   
current_orientation = "horizontal"  

def ensure_folder_exists():
    if not os.path.exists(SAVE_FOLDER):
        try:
            os.makedirs(SAVE_FOLDER)
            print(f"Created folder: {SAVE_FOLDER}")
        except Exception as e:
            print(f"Failed to create folder: {e}")
            return False
    return True

def get_next_filename():
    ensure_folder_exists()
    
    try:
        files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.jpg') and f[:-4].isdigit()]
        
        # If no files, start from 1
        if not files:
            return os.path.join(SAVE_FOLDER, "1.jpg")
        
        # Extract number parts and find the maximum
        max_num = max([int(f[:-4]) for f in files])
        next_num = max_num + 1
        
        return os.path.join(SAVE_FOLDER, f"{next_num}.jpg")
    except Exception as e:
        print(f"Error getting filename: {e}")
        # Use timestamp as backup filename
        timestamp = int(time.time())
        return os.path.join(SAVE_FOLDER, f"backup_{timestamp}.jpg")

def detect_strong_light(frame):
    """Detect strong light in the image"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate the ratio of pixels above the threshold
    bright_pixels = np.sum(gray > LIGHT_THRESHOLD)
    total_pixels = gray.size
    bright_ratio = bright_pixels / total_pixels
    
    # Return whether there is strong light
    has_strong_light = bright_ratio > BRIGHT_AREA_THRESHOLD
    return has_strong_light, bright_ratio

def resize_image(frame, orientation):
    """Resize image according to specified orientation"""
    if orientation == "horizontal":
        return cv2.resize(frame, HORIZONTAL_RESOLUTION)
    else:  # vertical
        return cv2.resize(frame, VERTICAL_RESOLUTION)

def save_image(frame, filename, orientation):
    """Save image to file without display text"""
    # Use a copy of the original frame
    clean_frame = frame.copy()
    
    # Resize the image
    resized_frame = resize_image(clean_frame, orientation)
    
    # Save the image
    try:
        cv2.imwrite(filename, resized_frame)
        print(f"Saved image: {os.path.basename(filename)}")
        return True
    except Exception as e:
        print(f"Failed to save image: {e}")
        return False

def add_display_info(frame, has_strong_light, bright_ratio, time_since_last_capture, stable_frames, waiting_for_light_change):
    """Add information text to the display frame without affecting saved images"""
    display_frame = frame.copy()
    
    # Add strong light detection status
    status_text = f"Light Detection: {'YES' if has_strong_light else 'NO'} ({bright_ratio*100:.1f}%)"
    cv2.putText(display_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
               0.7, (0, 0, 255) if has_strong_light else (0, 255, 0), 2)
    
    # Add cooldown time
    cooldown_text = f"Cooldown: {max(0, COOLDOWN_TIME - time_since_last_capture):.1f}s"
    cv2.putText(display_frame, cooldown_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Add orientation information
    orientation_text = f"Orientation: {'Horizontal' if current_orientation == 'horizontal' else 'Vertical'}"
    cv2.putText(display_frame, orientation_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    # Add frame count and mode information
    if waiting_for_light_change:
        mode_text = "Mode: Waiting for light change"
    else:
        mode_text = f"Mode: Counting stable frames {stable_frames}/{STABILITY_FRAMES}"
    cv2.putText(display_frame, mode_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
    
    return display_frame

def main():
    global current_orientation
    
    # Ensure folder exists
    if not ensure_folder_exists():
        print("Unable to create save folder, program exiting")
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("Cannot open camera, please check connection or change camera index")
        return
    
    # Get camera resolution
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {frame_width}x{frame_height}")
    
    print("Camera started, monitoring light...")
    print(f"Images will be saved to: {SAVE_FOLDER}")
    print(f"Light brightness threshold: {LIGHT_THRESHOLD}")
    print(f"Strong light area ratio threshold: {BRIGHT_AREA_THRESHOLD*100:.1f}%")
    print(f"Default photo orientation: {current_orientation} ({HORIZONTAL_RESOLUTION if current_orientation == 'horizontal' else VERTICAL_RESOLUTION})")
    print("Press 'o' to switch orientation, 'c' to take photo manually, ESC to exit")
    
    # Status variables
    last_capture_time = 0
    stable_dark_frames = 0  # Count of consecutive dark frames
    was_bright = False  # Initial state set to no strong light
    initial_capture_done = False  # Track if we've already captured the initial photo
    waiting_for_light_change = False  # Flag to indicate we're waiting for light to change from bright to dark
    
    try:
        while True:
            # Read a frame
            ret, frame = cap.read()
            if not ret:
                print("Cannot get image, exiting program")
                break
            
            # Detect strong light
            has_strong_light, bright_ratio = detect_strong_light(frame)
            
            current_time = time.time()
            time_since_last_capture = current_time - last_capture_time
            
            # Add information to display frame
            display_frame = add_display_info(frame, has_strong_light, bright_ratio, 
                                            time_since_last_capture, stable_dark_frames, 
                                            waiting_for_light_change)
            
            # Show real-time display (with text information)
            cv2.imshow("Camera Light Monitor", display_frame)
            
            # State machine logic
            if not initial_capture_done:
                # Initial state: Counting frames until first capture
                if not has_strong_light:
                    stable_dark_frames += 1
                    if stable_dark_frames >= STABILITY_FRAMES and time_since_last_capture >= COOLDOWN_TIME:
                        # Take the initial photo
                        filename = get_next_filename()
                        save_image(frame, filename, current_orientation)
                        last_capture_time = current_time
                        stable_dark_frames = 0
                        initial_capture_done = True
                        waiting_for_light_change = True
                        print("Initial capture complete. Now waiting for light to change.")
                else:
                    stable_dark_frames = 0
            
            elif waiting_for_light_change:
                # Wait for light to change from bright to dark
                if has_strong_light:
                    was_bright = True
                elif was_bright and not has_strong_light:
                    # Light changed from bright to dark
                    stable_dark_frames += 1
                    if stable_dark_frames >= STABILITY_FRAMES and time_since_last_capture >= COOLDOWN_TIME:
                        # Take photo after light change
                        filename = get_next_filename()
                        save_image(frame, filename, current_orientation)
                        last_capture_time = current_time
                        stable_dark_frames = 0
                        was_bright = False
                        print("Light change capture complete. Waiting for next light change.")
                elif not has_strong_light and not was_bright:
                    # Still dark, but we're waiting for it to be bright first
                    pass
                else:
                    stable_dark_frames = 0
            
            # Key handling
            key = cv2.waitKey(1)
            if key == 27:  # ESC key
                break
            elif key == ord('c'):  # Press C to take photo manually
                filename = get_next_filename()
                save_image(frame, filename, current_orientation)
                print(f"Manual capture: {os.path.basename(filename)}")
                last_capture_time = current_time
            elif key == ord('o'):  # Press O to switch orientation
                current_orientation = "vertical" if current_orientation == "horizontal" else "horizontal"
                print(f"Switched orientation to: {current_orientation}")
            elif key == ord('r'):  # Press R to reset the state machine
                initial_capture_done = False
                waiting_for_light_change = False
                stable_dark_frames = 0
                was_bright = False
                print("State machine reset. Starting over.")
    
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        print("Program exited")

if __name__ == "__main__":
    main()