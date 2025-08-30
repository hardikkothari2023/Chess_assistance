# assistant.py

import time
import logging
from config import CAPTURE_INTERVAL
from recognition import BoardRecognizer
from engine import Engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s -[%(levelname)s]- %(message)s')

def validate_fen(fen_pieces):
    """Checks if a FEN has both kings."""
    return fen_pieces.count('K') == 1 and fen_pieces.count('k') == 1

def main():
    """Main function for the dynamic chess assistant."""
    recognizer = BoardRecognizer()
    stockfish_engine = Engine()

    # Initialization
    if not recognizer.load_templates(): return
    if not stockfish_engine.startup(): return
    if not recognizer.select_board_region(): return
    
    is_flipped = 'y' in input("Are you playing as Black (board is flipped)? [y/N]: ").lower()
    
    print("\n✅ Assistant started. Watching for board changes...")
    last_fen = None

    try:
        while True:
            current_fen = recognizer.image_to_fen_pieces(is_flipped)
            
            if current_fen and current_fen != last_fen:
                print("\n" + "="*70)
                print(f"✅ New Position Detected: {current_fen}")
                
                if not validate_fen(current_fen):
                    logging.warning(f"Invalid board state recognized. Missing King(s).")
                    print("⚠️ Invalid board state recognized. Please adjust CONFIDENCE_THRESHOLD in config.py")
                    last_fen = current_fen
                    continue

                # Since we are stateless, we must ask for the turn
                turn_input = input("Whose turn is it to move? [white/black]: ").lower()
                turn_char = 'b' if 'b' in turn_input else 'w'
                
                print("Analyzing...")
                best_move, top_moves_str = stockfish_engine.get_best_move(current_fen, turn_char)
                
                print(f"♟️ Best Move: {best_move}")
                print(f"📊 Top Moves: {top_moves_str}")
                print("="*70)

                last_fen = current_fen
            
            time.sleep(CAPTURE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        stockfish_engine.shutdown()

if __name__ == "__main__":
    main()