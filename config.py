# # config.py
# # -------------------------
# # Stockfish Engine Settings
# # -------------------------
# # IMPORTANT: Update this path to the location of your Stockfish executable
# STOCKFISH_PATH = r"stockfish.exe" # <-- CHANGE THIS
# # Example for Windows: "C:/Users/YourUser/Downloads/stockfish/stockfish.exe"
# # Example for Linux/Mac: "/usr/local/bin/stockfish"

# # Set the thinking time for the engine in seconds
# STOCKFISH_THINK_TIME = 1.0

# # Set the engine depth (higher is stronger but slower)
# STOCKFISH_DEPTH = 5


# # -------------------------
# # Board Recognition Settings
# # -------------------------
# # The directory containing piece templates (e.g., 'pieces/chesscom_light/')
# PIECE_THEME = 'pieces/my_pieces'

# # The confidence threshold for template matching (0.0 to 1.0)
# # A lower value may lead to more false positives; a higher value may miss pieces.
# CONFIDENCE_THRESHOLD = 0.7


# # -------------------------
# # Real-Time Loop Settings
# # -------------------------
# # Delay in seconds between screen captures to reduce CPU usage
# CAPTURE_INTERVAL = 1.5

# # -------------------------
# # Debugging Settings
# # -------------------------
# # Set to True to save screenshots and log detailed information
# DEBUG_MODE = True
# DEBUG_DIR = "debug"
# LAST_BOARD_IMG_PATH = f"{DEBUG_DIR}/last_board.png"

# config.py - FINAL GUARANTEED VERSION

# -------------------------
# Stockfish Engine Settings
# -------------------------
# This is now the simplest possible path and will work correctly.
STOCKFISH_PATH = r"stockfish.exe"

# Set the thinking time for the engine in seconds
STOCKFISH_THINK_TIME = 1.0

# Set the engine depth
STOCKFISH_DEPTH = 12


# -------------------------
# Board Recognition Settings
# -------------------------
# This must point to the folder with YOUR 12 captured piece images
PIECE_THEME = 'pieces/my_pieces/'

# This is a balanced value that should work with your custom templates
CONFIDENCE_THRESHOLD = 0.75


# -------------------------
# Real-Time Loop Settings
# -------------------------
CAPTURE_INTERVAL = 1.5


# -------------------------
# Debugging Settings
# -------------------------
DEBUG_MODE = True
DEBUG_DIR = "debug"
LAST_BOARD_IMG_PATH = f"{DEBUG_DIR}/last_board.png"