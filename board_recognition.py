# board_recognition.py
import cv2
import numpy as np
import chess
import os
import logging
from config import PIECE_THEME, CONFIDENCE_THRESHOLD, DEBUG_MODE, LAST_BOARD_IMG_PATH

# Load piece templates
PIECE_TEMPLATES = {}
for filename in os.listdir(PIECE_THEME):
    if filename.endswith(".png"):
        piece_code = filename.split('.')[0]
        path = os.path.join(PIECE_THEME, filename)
        template = cv2.imread(path, cv2.IMREAD_COLOR)
        if template is None:
            logging.warning(f"Could not load template image: {path}")
            continue
        PIECE_TEMPLATES[piece_code] = template
        logging.info(f"Loaded template for piece: {piece_code}")

def find_chessboard(image):
    """
    Finds the largest square contour in the image, assumed to be the chessboard.
    Returns the cropped chessboard image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    largest_area = 0
    best_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > largest_area:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                largest_area = area
                best_contour = approx
    
    if best_contour is not None:
        x, y, w, h = cv2.boundingRect(best_contour)
        return image[y:y+h, x:x+w]
    
    logging.warning("Chessboard not detected.")
    return None

def identify_piece(square_img):
    """
    Identifies a piece on a given square image using template matching.
    """
    best_match = None
    max_val = CONFIDENCE_THRESHOLD  # Start with the threshold

    # Use the alpha channel for matching if available
    for piece_code, template in PIECE_TEMPLATES.items():
        # Ensure template is not larger than the square
        if template.shape[0] > square_img.shape[0] or template.shape[1] > square_img.shape[1]:
            continue

        res = cv2.matchTemplate(square_img, template, cv2.TM_CCOEFF_NORMED)
        _, current_max, _, _ = cv2.minMaxLoc(res)

        if current_max > max_val:
            max_val = current_max
            best_match = piece_code
            
    return best_match

def image_to_fen(image, is_flipped=False):
    """
    Converts a chessboard image to a FEN string.
    """
    board_img = find_chessboard(image)
    if board_img is None:
        return None

    if DEBUG_MODE:
        cv2.imwrite(LAST_BOARD_IMG_PATH, board_img)

    square_height = board_img.shape[0] // 8
    square_width = board_img.shape[1] // 8
    
    fen = ""
    for r in range(8):
        empty_count = 0
        for c in range(8):
            actual_r, actual_c = (7 - r, 7 - c) if is_flipped else (r, c)
            
            x1, y1 = actual_c * square_width, actual_r * square_height
            x2, y2 = x1 + square_width, y1 + square_height
            square = board_img[y1:y2, x1:x2]
            
            piece = identify_piece(square)
            
            if piece:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                
                piece_char = piece[1] # e.g., 'P' from 'wP'
                if piece[0] == 'b':
                    fen += piece_char.lower()
                else:
                    fen += piece_char.upper()
            else:
                empty_count += 1
        
        if empty_count > 0:
            fen += str(empty_count)
        if r < 7:
            fen += '/'
            
    # NOTE: This is a simplified FEN. It doesn't include turn, castling, en passant.
    # The engine can often work with just the board state, but for accuracy, this would
    # need to be tracked by comparing board states over time.
    fen += " w - - 0 1" # Assume it's white's turn with default rights for now.
    
    try:
        chess.Board(fen)
        logging.info(f"Generated valid FEN: {fen}")
        return fen
    except ValueError:
        logging.error(f"Generated invalid FEN: {fen}")
        return None