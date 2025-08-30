# recognition.py

import pyautogui
import cv2
import numpy as np
import os
import logging
from config import PIECE_THEME, CONFIDENCE_THRESHOLD

class BoardRecognizer:
    def __init__(self):
        self.board_region = None
        self.piece_templates = {}
        self.template_masks = {}

    def load_templates(self):
        """Loads piece templates and their transparency masks."""
        logging.info(f"Loading piece templates from: {PIECE_THEME}")
        try:
            for filename in os.listdir(PIECE_THEME):
                if filename.lower().endswith(".png"):
                    piece_code = os.path.splitext(filename)[0]
                    path = os.path.join(PIECE_THEME, filename)
                    template_rgba = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    
                    if template_rgba is None or template_rgba.shape[2] != 4:
                        logging.error(f"Template '{filename}' is not a valid PNG with transparency. Please recapture it.")
                        return False
                        
                    self.template_masks[piece_code] = template_rgba[:, :, 3]
                    self.piece_templates[piece_code] = template_rgba[:, :, :3]

            if len(self.piece_templates) < 12:
                logging.error(f"Failed to load all 12 templates from '{PIECE_THEME}'.")
                return False
            logging.info(f"Successfully loaded {len(self.piece_templates)} templates with masks.")
            return True
        except Exception as e:
            logging.error(f"Error loading templates from '{PIECE_THEME}': {e}")
            return False

    def select_board_region(self):
        """Lets the user select the board region."""
        logging.info("A window will appear. Draw a TIGHT rectangle on the 8x8 squares only, INSIDE the coordinates.")
        try:
            screenshot = pyautogui.screenshot()
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            roi = cv2.selectROI("Select Chessboard Region", img, fromCenter=False, showCrosshair=True)
            cv2.destroyAllWindows()
            if roi[2] == 0 or roi[3] == 0:
                logging.error("No region selected. Exiting.")
                return False
            self.board_region = roi
            logging.info(f"Capture region selected: {self.board_region}")
            return True
        except Exception as e:
            logging.error(f"Could not select region: {e}")
            return False

    def _identify_piece(self, square_img):
        """Identifies a piece using masked template matching."""
        best_match_piece = None
        max_score = CONFIDENCE_THRESHOLD
        h, w, _ = square_img.shape

        for piece_code, template in self.piece_templates.items():
            resized_template = cv2.resize(template, (w, h), interpolation=cv2.INTER_AREA)
            mask = self.template_masks[piece_code]
            resized_mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(square_img, resized_template, cv2.TM_CCOEFF_NORMED, mask=resized_mask)
            _, current_max, _, _ = cv2.minMaxLoc(res)
            
            if current_max > max_score:
                max_score = current_max
                best_match_piece = piece_code
        return best_match_piece

    def image_to_fen_pieces(self, is_flipped=False):
        """Captures the board and returns the piece placement part of the FEN."""
        if not self.board_region: return None
        screenshot = pyautogui.screenshot(region=self.board_region)
        board_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        square_h, square_w = board_img.shape[0] // 8, board_img.shape[1] // 8
        fen_rows = []
        for r in range(8):
            fen_row = ""
            empty_count = 0
            for c in range(8):
                square = board_img[r*square_h:(r+1)*square_h, c*square_w:(c+1)*square_w]
                piece = self._identify_piece(square)
                if piece:
                    if empty_count > 0: fen_row += str(empty_count)
                    empty_count = 0
                    piece_char = piece[1]
                    fen_row += piece_char.lower() if piece[0] == 'b' else piece_char.upper()
                else:
                    empty_count += 1
            if empty_count > 0: fen_row += str(empty_count)
            fen_rows.append(fen_row)
        
        fen = "/".join(fen_rows)
        return '/'.join(row[::-1] for row in fen.split('/')[::-1]) if is_flipped else fen