# screen_capture.py - NEW VERSION USING PILLOW

import cv2
import numpy as np
from PIL import ImageGrab
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CAPTURE_BBOX = None

def select_capture_region():
    """
    Takes a screenshot of the entire screen and lets the user select the
    chessboard area. Returns the bounding box coordinates.
    """
    global CAPTURE_BBOX

    # Grab the entire screen
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    img = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Let the user select the ROI
    cv2.putText(img, "Draw a rectangle around the chessboard and press ENTER", 
                (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    roi = cv2.selectROI("Select Chessboard Region", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    # roi = (x, y, w, h)
    # We need (left, top, right, bottom) for Pillow
    left, top, w, h = roi
    CAPTURE_BBOX = (left, top, left + w, top + h)

    logging.info(f"Capture region selected. Bounding box: {CAPTURE_BBOX}")
    return CAPTURE_BBOX

def capture_screen():
    """
    Captures the pre-defined screen region using Pillow.
    """
    if CAPTURE_BBOX is None:
        logging.error("Capture region is not set. Call select_capture_region() first.")
        return None

    try:
        screenshot = ImageGrab.grab(bbox=CAPTURE_BBOX)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        logging.info("Screenshot captured successfully with Pillow.")
        return img
    except Exception as e:
        logging.error(f"Failed to capture screen with Pillow: {e}")
        return None