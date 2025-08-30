import cv2
import numpy as np
import pyautogui
import os

# =============================
# CONFIG
# =============================
# Folder to save extracted templates
TEMPLATE_DIR = "pieces/my_pieces"
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Folder for debugging each square
DEBUG_DIR = "debug_squares"
os.makedirs(DEBUG_DIR, exist_ok=True)

# ROI of board (adjust if needed)
ROI_X, ROI_Y, ROI_W, ROI_H = 119, 247, 698, 690
ROWS, COLS = 8, 8

# Threshold for matching
MATCH_THRESHOLD = 0.55


def capture_board():
    """Capture board screenshot and return image."""
    screenshot = pyautogui.screenshot(region=(ROI_X, ROI_Y, ROI_W, ROI_H))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img


def split_squares(board_img):
    """Split board into 8x8 squares and save debug squares."""
    h, w = board_img.shape[:2]
    square_h, square_w = h // ROWS, w // COLS
    squares = []

    for row in range(ROWS):
        row_squares = []
        for col in range(COLS):
            y1, y2 = row * square_h, (row + 1) * square_h
            x1, x2 = col * square_w, (col + 1) * square_w
            square = board_img[y1:y2, x1:x2]

            # Save debug
            cv2.imwrite(f"{DEBUG_DIR}/{row}_{col}.png", square)

            row_squares.append(square)
        squares.append(row_squares)

    return squares


def save_unique_templates(squares):
    """Automatically detect unique pieces and save them as templates."""
    existing_templates = []

    for row in range(ROWS):
        for col in range(COLS):
            square = squares[row][col]
            square_gray = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)

            # Skip if square is basically empty background
            if np.mean(square_gray) > 230:  # very white
                continue

            found = False
            for idx, temp in enumerate(existing_templates):
                res = cv2.matchTemplate(square_gray, temp, cv2.TM_CCOEFF_NORMED)
                if np.max(res) > MATCH_THRESHOLD:
                    found = True
                    break

            if not found:
                # Save as new template
                filename = f"{TEMPLATE_DIR}/piece_{len(existing_templates)}.png"
                cv2.imwrite(filename, square_gray)
                existing_templates.append(square_gray)
                print(f"Saved new piece template: {filename}")


def main():
    print("📸 Capturing board...")
    board_img = capture_board()

    print("🔲 Splitting into squares...")
    squares = split_squares(board_img)

    print("♟ Extracting unique pieces...")
    save_unique_templates(squares)

    print("✅ Done! Templates saved in:", TEMPLATE_DIR)
    print("👉 Next run, you can use these templates for recognition.")


if __name__ == "__main__":
    main()
