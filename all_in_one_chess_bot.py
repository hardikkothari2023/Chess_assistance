# assistant.py - The Final, Dynamic, and Robust Folder-Based Version

import pyautogui
import cv2
import numpy as np
import chess
import chess.engine
import os
import time
import logging

# -----------------------------------------------------------------------------------
# --- CONFIGURATION ---
# -----------------------------------------------------------------------------------
# THIS MUST BE THE SIMPLE PATH to the .exe file in your project folder.
STOCKFISH_PATH = r"C:\Users\HARDIK\OneDrive\Desktop\Chess_assistance\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

# This MUST be the path to your folder of 12 transparent PNG images.
PIECE_THEME = 'pieces/my_pieces/'

# THIS IS THE MOST IMPORTANT SETTING TO TUNE.
# If it misses pieces, LOWER this value (e.g., to 0.65).
# If it sees pieces that aren't there, RAISE this value (e.g., to 0.75).
CONFIDENCE_THRESHOLD = 0.32

CAPTURE_INTERVAL = 1.5
STOCKFISH_THINK_TIME = 1.0
# -----------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s -[%(levelname)s]- %(message)s')

class ChessAssistant:
    def __init__(self, config):
        self.config = config
        self.board_region = None
        self.engine = None
        self.piece_templates = {}
        self.template_masks = {}
        self.is_playing_as_black = False

    def setup(self):
        return self._load_templates() and self._init_stockfish() and self._select_board_region()
            
    def _load_templates(self):
        theme_path = self.config['PIECE_THEME']
        logging.info(f"Loading piece templates from: {theme_path}")
        try:
            for filename in os.listdir(theme_path):
                if filename.lower().endswith(".png"):
                    piece_code = os.path.splitext(filename)[0]
                    path = os.path.join(theme_path, filename)
                    template_rgba = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if template_rgba is None or template_rgba.shape[2] != 4:
                        logging.error(f"Template '{filename}' is not a valid PNG with transparency. Please recapture it.")
                        return False
                    self.template_masks[piece_code] = template_rgba[:, :, 3]
                    self.piece_templates[piece_code] = template_rgba[:, :, :3]
            if len(self.piece_templates) < 12:
                logging.error(f"Failed to load all 12 templates from '{theme_path}'.")
                return False
            logging.info(f"Successfully loaded {len(self.piece_templates)} templates with masks.")
            return True
        except Exception as e:
            logging.error(f"Error loading templates from '{theme_path}': {e}")
            return False

    def _init_stockfish(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.config['STOCKFISH_PATH'])
            logging.info(f"Stockfish engine initialized successfully with path: {self.config['STOCKFISH_PATH']}")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Stockfish: {e}")
            return False

    def _select_board_region(self):
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
        best_match_piece = None
        max_score = self.config['CONFIDENCE_THRESHOLD']
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

    def _image_to_fen_pieces(self):
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
        return '/'.join(row[::-1] for row in fen.split('/')[::-1]) if self.is_playing_as_black else fen
    
    def _validate_fen(self, fen_pieces):
        return fen_pieces.count('K') == 1 and fen_pieces.count('k') == 1

    def _get_best_move(self, fen_pieces, turn_char):
        try:
            # For stateless analysis, we assume default castling rights.
            full_fen = f"{fen_pieces} {turn_char} KQkq - 0 1"
            board = chess.Board(full_fen)
            limit = chess.engine.Limit(time=self.config['STOCKFISH_THINK_TIME'])
            info = self.engine.analyse(board, limit, multipv=3)
            if not info: return "No moves found", ""
            top_moves = []
            for item in info:
                move = item.get('pv', [None])[0]
                if move is None: continue
                score = item['score'].pov(board.turn)
                eval_str = f"Mate in {score.mate()}" if score.is_mate() else f"{score.score() / 100.0:+.2f}"
                top_moves.append(f"{move.uci()} (Eval: {eval_str})")
            return top_moves[0].split(' ')[0], " | ".join(top_moves)
        except Exception as e:
            logging.error(f"Engine analysis failed: {e}")
            return "Analysis Error", ""

    def run(self):
        if not self.setup():
            input("Initialization failed. Press Enter to exit.")
            return
            
        self.is_playing_as_black = 'y' in input("Are you playing as Black (board is flipped)? [y/N]: ").lower()
        
        print("\n✅ Assistant started. Watching for board changes...")
        last_fen = None

        try:
            while True:
                current_fen = self._image_to_fen_pieces()
                if current_fen and current_fen != last_fen:
                    print("\n" + "="*70)
                    print(f"✅ New Position Detected: {current_fen}")
                    
                    if not self._validate_fen(current_fen):
                        logging.warning(f"Invalid board state recognized. Missing King(s).")
                        print("⚠️ Invalid board state recognized. Please adjust CONFIDENCE_THRESHOLD.")
                        last_fen = current_fen
                        continue

                    turn_input = input("Whose turn is it to move? [white/black]: ").lower()
                    turn_char = 'b' if 'b' in turn_input else 'w'
                    
                    print("Analyzing...")
                    best_move, top_moves_str = self._get_best_move(current_fen, turn_char)
                    
                    print(f"♟️ Best Move: {best_move}")
                    print(f"📊 Top Moves: {top_moves_str}")
                    print("="*70)
                    last_fen = current_fen
                time.sleep(self.config['CAPTURE_INTERVAL'])
        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
        finally:
            if self.engine: self.engine.quit()

if __name__ == "__main__":
    config = {
        "STOCKFISH_PATH": STOCKFISH_PATH, "PIECE_THEME": PIECE_THEME,
        "CONFIDENCE_THRESHOLD": CONFIDENCE_THRESHOLD, "CAPTURE_INTERVAL": CAPTURE_INTERVAL,
        "STOCKFISH_THINK_TIME": STOCKFISH_THINK_TIME
    }
    assistant = ChessAssistant(config)
    assistant.run()