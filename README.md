# ♟️ Real-Time Chess Assistant

Analyze your online chess games in real-time using screen recognition and the Stockfish engine.

This Python-based assistant continuously watches a selected portion of your screen, recognizes the state of the chessboard, and uses the powerful Stockfish engine to suggest the best possible move. It is designed to be fully automatic after an initial setup, intelligently tracking the game state move by move.



---

## ✨ Features

* **Real-Time Analysis:** Automatically detects when a move is made and provides instant feedback.
* **Screen-Based Recognition:** Works with any online chess platform (like Chess.com or Lichess) by looking at your screen. No API needed.
* **Powerful Engine:** Integrates with the world-class Stockfish chess engine for grandmaster-level analysis.
* **Intelligent Game Tracking:** Keeps an internal model of the game, correctly tracking the turn, castling rights, and other rules.
* **Robust and Self-Correcting:** Includes failsafes to handle bad screen reads and re-synchronize with the game if it gets confused.
* **Customizable:** Works with any piece and board theme by using user-provided template images. Displays the top 3 moves with evaluations.

---

## 📂 Project Structure

The project uses a simple, single-script structure supported by a few key assets.
