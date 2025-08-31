# assistant.py - The Final Version with First-Move Suggestion

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
# This path MUST be simple, pointing to the .exe file in your project folder.
STOCKFISH_PATH = r"C:\Users\HARDIK\OneDrive\Desktop\Chess_assistance\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

# This path MUST point to your folder of 12 transparent PNG images.
PIECE_THEME = 'pieces/my_pieces/'

# This is the most important setting to tune.
# If it misses pieces, LOWER this value (e.g., to 0.65).
# If it sees pieces that aren't there, RAISE this value (e.g., to 0.75).
CONFIDENCE_THRESHOLD = 0.3

CAPTURE_INTERVAL = 1.5
STOCKFISH_THINK_TIME = 5.0
# -----------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s -[%(levelname)s]- %(message)s')

class ChessAssistant:
    def __init__(self, config):
        self.config = config
        self.board_region = None
        self.engine = None
        self.piece_templates = {}
        self.template_masks = {}
        self.internal_board = chess.Board()
        self.is_playing_as_black = False

    def setup(self):
        """Runs all necessary setup functions."""
        return self._load_templates() and self._init_stockfish() and self._select_board_region()
            
    def _load_templates(self):
        """Loads piece templates and their transparency masks."""
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
        """Initializes the Stockfish engine."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.config['STOCKFISH_PATH'])
            logging.info("Stockfish engine initialized successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Stockfish: {e}")
            return False

    def _select_board_region(self):
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
        return '/'.join(row[::-1] for row in fen.split('/')[::-1]) if self.is_playing_as_black else fen
    
    def _validate_fen(self, fen_pieces):
        """Checks if a FEN has both kings."""
        return fen_pieces.count('K') == 1 and fen_pieces.count('k') == 1

    def _find_played_move(self, new_fen_pieces):
        """Finds the legal move that transitions the internal board to the new FEN."""
        for move in self.internal_board.legal_moves:
            self.internal_board.push(move)
            if self.internal_board.fen().split(' ')[0] == new_fen_pieces:
                self.internal_board.pop()
                return move
            self.internal_board.pop()
        return None
    
    def _get_best_move(self):
        """Gets the best move for the current internal board state."""
        try:
            limit = chess.engine.Limit(time=self.config['STOCKFISH_THINK_TIME'])
            info = self.engine.analyse(self.internal_board, limit, multipv=3)
            if not info: return None, "No moves found"
            top_moves = []
            for item in info:
                move = item.get('pv', [None])[0]
                if move is None: continue
                score = item['score'].pov(self.internal_board.turn)
                eval_str = f"Mate in {score.mate()}" if score.is_mate() else f"{score.score() / 100.0:+.2f}"
                top_moves.append(f"{move.uci()} (Eval: {eval_str})")
            return top_moves[0].split(' ')[0], " | ".join(top_moves)
        except Exception as e:
            logging.error(f"Engine analysis failed: {e}")
            return None, "Analysis Error"

    def run(self):
        """The main loop of the chess assistant."""
        if not self.setup():
            input("Initialization failed. Press Enter to exit.")
            return

        self.is_playing_as_black = 'y' in input("Are you playing as Black (board is flipped)? [y/N]: ").lower()

        print("\n✅ Assistant ready. Please set up the board to the starting position of your game.")
        input("--> Press ENTER when the starting position is on the screen...")
        
        initial_fen_pieces = self._image_to_fen_pieces()
        if not self._validate_fen(initial_fen_pieces):
            print(f"⚠️ Could not recognize a valid initial board. Detected: {initial_fen_pieces}")
            print("This is a CALIBRATION issue. Try adjusting CONFIDENCE_THRESHOLD at the top of the script and restart.")
            return
            
        self.internal_board = chess.Board(initial_fen_pieces)
        print(f"✅ Initial position recognized: {initial_fen_pieces}")

        # --- NEW LOGIC TO SUGGEST THE FIRST MOVE ---
        if not self.is_playing_as_black and self.internal_board.turn == chess.WHITE:
            print("\n" + "="*70)
            print("It's your turn to move (White). Analyzing opening move...")
            best_move, top_moves_str = self._get_best_move()
            if best_move:
                print(f"♟️ Best Opening Move: {best_move}")
                print(f"📊 Top Moves: {top_moves_str}")
            print("="*70)
        # -------------------------------------------

        print("\nWatching for moves...")
        
        try:
            while True:
                time.sleep(self.config['CAPTURE_INTERVAL'])
                current_fen_pieces = self._image_to_fen_pieces()
                
                if current_fen_pieces and current_fen_pieces != self.internal_board.fen().split(' ')[0]:
                    print("\n" + "="*70)
                    logging.info("Change detected. Analyzing...")
                    if not self._validate_fen(current_fen_pieces):
                        logging.warning(f"Bad recognition detected: {current_fen_pieces}. Waiting for clearer view.")
                        continue

                    move_played = self._find_played_move(current_fen_pieces)
                    if move_played:
                        self.internal_board.push(move_played)
                        print(f"✅ Move Detected: {move_played.uci()}")
                        is_my_turn = (not self.is_playing_as_black and self.internal_board.turn == chess.WHITE) or \
                                     (self.is_playing_as_black and self.internal_board.turn == chess.BLACK)
                        if is_my_turn:
                            print("Analyzing for your best move...")
                            best_move, top_moves_str = self._get_best_move()
                            if best_move:
                                print(f"♟️ Best Move: {best_move}")
                                print(f"📊 Top Moves: {top_moves_str}")
                            else:
                                print(f"⚠️ Could not retrieve analysis. Reason: {top_moves_str}")
                        else:
                            print("Opponent is thinking...")
                    else:
                        print("⚠️ Could not determine last move. Re-synchronizing.")
                        self.internal_board.set_fen(current_fen_pieces)
                    print("="*70)
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