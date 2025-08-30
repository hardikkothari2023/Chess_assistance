# config.py

# 1. This MUST be the simple path to the .exe file in your project folder.
STOCKFISH_PATH = r"Chess_assistance\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

# 2. This MUST be the path to your folder of 12 transparent PNG images.
PIECE_THEME = 'pieces/my_pieces/'

# 3. This is the most important setting to tune for recognition.
#    If it misses pieces, LOWER this value (e.g., to 0.65).
#    If it sees pieces that aren't there, RAISE this value (e.g., to 0.75).
CONFIDENCE_THRESHOLD = 0.7

# 4. Time in seconds between screen captures.
CAPTURE_INTERVAL = 1.5

# 5. Time in seconds for the engine to think.
STOCKFISH_THINK_TIME = 1.0