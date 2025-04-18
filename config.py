import pygame

# Game constants
BOARD_SIZE = 8
CELL_SIZE = 80
TRAY_HEIGHT = 120
UI_MARGIN = 20
UI_HEADER_HEIGHT = 60  # Height for the header area with buttons and score

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Button colors
DETONATE_COLOR = (200, 0, 0)  # Darker red
DETONATE_HOVER = (180, 0, 0)  # Even darker red
UNDO_COLOR = (0, 0, 200)     # Darker blue
UNDO_HOVER = (0, 0, 180)     # Even darker blue
BUTTON_SHADOW = (100, 100, 100)  # Shadow color

# Piece types
HORIZONTAL = "horizontal"
DIAGONAL = "diagonal"

# Button dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
BUTTON_SHADOW_OFFSET = 2  # Shadow offset in pixels

# Calculate window dimensions
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + 2 * UI_MARGIN
WINDOW_HEIGHT = UI_HEADER_HEIGHT + BOARD_SIZE * CELL_SIZE + TRAY_HEIGHT + 3 * UI_MARGIN

# Calculate header positions
HEADER_Y = UI_MARGIN
HEADER_WIDTH = WINDOW_WIDTH - 2 * UI_MARGIN

# Calculate element positions in header
SCORE_X = UI_MARGIN
SCORE_Y = HEADER_Y + (UI_HEADER_HEIGHT - BUTTON_HEIGHT) // 2 + (BUTTON_HEIGHT - 36) // 2  # Align with button text

DETONATE_BUTTON_X = (WINDOW_WIDTH - BUTTON_WIDTH) // 2
DETONATE_BUTTON_Y = HEADER_Y + (UI_HEADER_HEIGHT - BUTTON_HEIGHT) // 2

UNDO_BUTTON_X = WINDOW_WIDTH - UI_MARGIN - BUTTON_WIDTH
UNDO_BUTTON_Y = HEADER_Y + (UI_HEADER_HEIGHT - BUTTON_HEIGHT) // 2

# Calculate board position
BOARD_X = UI_MARGIN
BOARD_Y = HEADER_Y + UI_HEADER_HEIGHT + UI_MARGIN

# Calculate tray position
TRAY_Y = BOARD_Y + BOARD_SIZE * CELL_SIZE + UI_MARGIN 