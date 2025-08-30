# engine.py

import chess
import chess.engine
import logging
from config import STOCKFISH_PATH, STOCKFISH_THINK_TIME

class Engine:
    def __init__(self):
        self.engine = None
    
    def startup(self):
        """Initializes the Stockfish engine."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            logging.info("Stockfish engine initialized successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Stockfish: {e}")
            return False

    def get_best_move(self, fen_pieces, turn_char):
        """Gets the best move from a FEN and turn."""
        try:
            # For stateless analysis, we assume default castling rights.
            full_fen = f"{fen_pieces} {turn_char} KQkq - 0 1"
            board = chess.Board(full_fen)
            
            limit = chess.engine.Limit(time=STOCKFISH_THINK_TIME)
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

    def shutdown(self):
        """Closes the Stockfish engine process."""
        if self.engine:
            self.engine.quit()
            logging.info("Stockfish engine closed.")