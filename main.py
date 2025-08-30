# main.py
import time
import logging
import os

from screen_capture import select_capture_region, capture_screen
from board_recognition import image_to_fen
from engine import init_stockfish, get_best_move, close_stockfish
from config import CAPTURE_INTERVAL, DEBUG_MODE, DEBUG_DIR

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    The main loop for the real-time chess assistant.
    """
    # Create debug directory if it doesn't exist
    if DEBUG_MODE and not os.path.exists(DEBUG_DIR):
        os.makedirs(DEBUG_DIR)
        
    # --- Initialization ---
    if not init_stockfish():
        return # Exit if Stockfish can't be started

    print("-----------------------------------------")
    print("      Real-Time Chess Assistant")
    print("-----------------------------------------")
    print("Please select the chessboard region on your screen.")
    
    capture_region = select_capture_region()
    if not capture_region:
        print("No region selected. Exiting.")
        return

    # Ask user if the board is flipped (playing as black)
    flip_input = input("Are you playing as Black? (Is the board flipped?) [y/N]: ").lower()
    is_flipped = flip_input == 'y'

    print("\nAssistant started. Watching the board...")
    
    last_fen = None

    try:
        while True:
            screenshot = capture_screen()
            if screenshot is None:
                time.sleep(CAPTURE_INTERVAL)
                continue

            current_fen = image_to_fen(screenshot, is_flipped)
            
            # Check if board state is valid and has changed
            if current_fen and current_fen != last_fen:
                print("\n" + "="*40)
                print(f"✅ Detected Position: {current_fen.split(' ')[0]}")
                last_fen = current_fen
                
                best_move, evaluation = get_best_move(current_fen)
                
                if best_move and evaluation:
                    print(f"♟️ Best Move: {best_move}")
                    print(f"📊 Evaluation: {evaluation}")
                else:
                    print("Could not retrieve engine analysis.")
                print("="*40)

            # Wait before the next capture to avoid high CPU usage
            time.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        close_stockfish()

if __name__ == "__main__":
    main()