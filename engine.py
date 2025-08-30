# engine.py
import chess
import chess.engine
import logging
from config import STOCKFISH_PATH, STOCKFISH_THINK_TIME, STOCKFISH_DEPTH

ENGINE = None

def init_stockfish():
    """
    Initializes the Stockfish engine process.
    Returns True on success, False on failure.
    """
    global ENGINE
    try:
        ENGINE = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        logging.info(f"Stockfish engine initialized successfully from: {STOCKFISH_PATH}")
        return True
    except FileNotFoundError:
        logging.error(f"Stockfish executable not found at: {STOCKFISH_PATH}")
        logging.error("Please update STOCKFISH_PATH in config.py")
        return False

def get_best_move(fen):
    """
    Gets the best move and evaluation from Stockfish for a given FEN.
    """
    if ENGINE is None:
        logging.error("Stockfish engine is not initialized.")
        return None, None

    try:
        board = chess.Board(fen)
        # You might need to determine whose turn it is from board state changes
        # For now, we set it based on the FEN, but this can be improved.
        if " b " in fen:
            board.turn = chess.BLACK
        else:
            board.turn = chess.WHITE

        result = ENGINE.analyse(board, chess.engine.Limit(time=STOCKFISH_THINK_TIME, depth=STOCKFISH_DEPTH))
        
        best_move = result['pv'][0]
        score = result['score'].relative

        eval_str = ""
        if score.is_mate():
            eval_str = f"Mate in {score.mate()}"
        else:
            cp = score.score() / 100.0
            eval_str = f"{cp:+.2f}"
            
        logging.info(f"Engine analysis: Best move {best_move}, Eval {eval_str}")
        return best_move, eval_str
        
    except Exception as e:
        logging.error(f"An error occurred during engine analysis: {e}")
        return None, None

def close_stockfish():
    """
    Closes the Stockfish engine process.
    """
    if ENGINE:
        ENGINE.quit()
        logging.info("Stockfish engine closed.")