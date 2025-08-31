# ♟️ All-in-One Chess Bot  

An advanced **real-time chess assistant** that helps you play smarter by analyzing the chessboard directly from your screen.  
The bot captures your chessboard, identifies all pieces using image recognition, and suggests the **best possible move**.  

---

## 🚀 Features  
- 📸 **Real-time Board Detection** – Automatically detects the chessboard from your screen.  
- ♞ **Piece Recognition** – Identifies every piece using pre-trained templates (works for both black and white).  
- 🤖 **Best Move Recommendation** – Suggests the strongest move using a chess engine.  
- 🖥️ **Cross-Platform** – Works on Windows, Linux, and macOS.  
- 🎥 **Demo Support** – You can attach a video walkthrough of the bot in action.  

---

## 🛠️ Tech Stack  
- **Python** (Core Language)  
- **OpenCV** – Image recognition & board detection  
- **Pillow (PIL)** – Image processing  
- **Stockfish** – Chess engine for best-move calculation  
- **PyAutoGUI** – For capturing screen input  
- **Base64 Encoded Templates** – Stores chess pieces securely without external files  

---

## 📂 Project Structure  

```bash
📦 All-in-One-Chess-Bot
├── pieces/                # Base64 encoded chess pieces (auto-generated at runtime)
├── extract_pieces.py      # Extracts and saves templates from Base64
├── detect_board.py        # Detects and processes the chessboard
├── recognize_pieces.py    # Identifies pieces on board
├── chess_engine.py        # Integrates with Stockfish for move suggestion
├── all_in_one_bot.py      # Main entry point (run this file)
└── README.md              # Project documentation
