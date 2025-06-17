# Import necessary libraries
import pygame
import sys

# PyGame Initialization
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 650
LEFT_PADDING = 30
TOP_PADDING = 45
GRID_WIDTH = WIDTH - 2 * LEFT_PADDING
GRID_HEIGHT = GRID_WIDTH
GRID_SIZE = 9
CELL_SIZE = GRID_WIDTH // GRID_SIZE
MAX_MISTAKES = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
DARK_BLUE = (0, 0, 200)

# Fonts & Buttons
BUTTON_FONT = pygame.font.SysFont("Segoe UI Emoji", 24)
RESET_BUTTON = pygame.Rect(LEFT_PADDING, HEIGHT - 50, 100, 40)
SOLVE_BUTTON = pygame.Rect(WIDTH - LEFT_PADDING - 100, HEIGHT - 50, 100, 40)

# Setup window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Timer & clock
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

# Game State
board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]
user_board = [row[:] for row in board]
selected_cell = None
invalid_cells = set()
mistakes = 0
game_over = False
sol_check = False
final_time = 0


# Utility Functions

def get_clicked_cell(pos):
    """Convert mouse position to grid cell, if within bounds."""
    x, y = pos
    if LEFT_PADDING <= x < LEFT_PADDING + GRID_WIDTH and TOP_PADDING <= y < TOP_PADDING + GRID_HEIGHT:
        col = (x - LEFT_PADDING) // CELL_SIZE
        row = (y - TOP_PADDING) // CELL_SIZE
        return row, col
    return None


def check_valid(bd, row, col, num):
    """Check if placing 'num' at (row, col) is valid."""
    if any(bd[row][j] == num and j != col for j in range(GRID_SIZE)):
        return False
    if any(bd[i][col] == num and i != row for i in range(GRID_SIZE)):
        return False

    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if bd[i][j] == num and (i, j) != (row, col):
                return False
    return True


def find_empty(bd):
    """Find the next empty cell in the board."""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if bd[i][j] == 0:
                return i, j
    return None


def solve(bd):
    """Solve the board using backtracking."""
    empty = find_empty(bd)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        bd[row][col] = num
        if check_valid(bd, row, col, num) and solve(bd):
            return True
        bd[row][col] = 0
    return False


# Drawing Functions

def draw_grid():
    for i in range(GRID_SIZE + 1):
        line_width = 4 if i % 3 == 0 else 1
        x = LEFT_PADDING + i * CELL_SIZE
        y = TOP_PADDING + i * CELL_SIZE
        pygame.draw.line(WIN, BLACK, (x, TOP_PADDING), (x, TOP_PADDING + GRID_HEIGHT), line_width)
        pygame.draw.line(WIN, BLACK, (LEFT_PADDING, y), (LEFT_PADDING + GRID_WIDTH, y), line_width)


def draw_numbers():
    font = pygame.font.SysFont("comicsans", 40)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            val = board[i][j] if board[i][j] != 0 else user_board[i][j]
            if val != 0:
                if (i, j) in invalid_cells:
                    color = RED
                elif board[i][j] == 0:
                    color = BLUE
                else:
                    color = BLACK
                    
                x = LEFT_PADDING + j * CELL_SIZE + 20
                y = TOP_PADDING + i * CELL_SIZE
                text = font.render(str(val), True, color)
                WIN.blit(text, (x, y))


def draw_selection():
    if selected_cell:
        row, col = selected_cell
        x = LEFT_PADDING + col * CELL_SIZE
        y = TOP_PADDING + row * CELL_SIZE
        pygame.draw.rect(WIN, LIGHT_BLUE, (x, y, CELL_SIZE, CELL_SIZE), 3)

def draw_buttons():
    pygame.draw.rect(WIN, GREEN, RESET_BUTTON)
    pygame.draw.rect(WIN, DARK_BLUE, SOLVE_BUTTON)
    WIN.blit(BUTTON_FONT.render("Reset", True, WHITE), (RESET_BUTTON.x + 20, RESET_BUTTON.y + 10))
    WIN.blit(BUTTON_FONT.render("Solve", True, WHITE), (SOLVE_BUTTON.x + 20, SOLVE_BUTTON.y + 10))


def draw_mistakes():
    text = BUTTON_FONT.render(f"Mistakes: {mistakes}/{MAX_MISTAKES}", True, RED)
    WIN.blit(text, (WIDTH - 170, 10))


def draw_timer():
    elapsed = (pygame.time.get_ticks() - start_time) // 1000 if not sol_check and not game_over else final_time
    minutes, seconds = divmod(elapsed, 60)
    time_str = f"\u23F1  {minutes:02}:{seconds:02}"
    WIN.blit(BUTTON_FONT.render(time_str, True, BLACK), (LEFT_PADDING, 10))


def draw_window():
    WIN.fill(WHITE)
    draw_timer()
    draw_mistakes()
    draw_grid()
    draw_numbers()
    draw_selection()
    draw_buttons()

    if game_over:
        overlay = pygame.Surface((GRID_WIDTH + 8, GRID_HEIGHT + 8))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        WIN.blit(overlay, (LEFT_PADDING - 2, TOP_PADDING - 2))
        font = pygame.font.SysFont("comicsans", 50)
        msg = font.render("Game Over!", True, RED)
        WIN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 25))

    pygame.display.update()
    
# Board Actions

def handle_reset():
    """Handles the reset logic when the reset button is clicked."""
    global selected_cell, mistakes, game_over, sol_check, final_time, start_time

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == 0:
                user_board[i][j] = 0

    selected_cell = None
    invalid_cells.clear()
    mistakes = 0
    game_over = False
    sol_check = False
    final_time = 0
    start_time = pygame.time.get_ticks()

def handle_solve():
    """Solves the puzzle using the backtracking solver."""
    global sol_check, final_time
    board_copy = [row[:] for row in board]

    if solve(board_copy):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if board[i][j] == 0:
                    user_board[i][j] = board_copy[i][j]                    
        invalid_cells.clear()
        sol_check = True
        final_time = (pygame.time.get_ticks() - start_time) // 1000

# Event Handlers 

def handle_mouse_click(pos):
    global selected_cell

    if RESET_BUTTON.collidepoint(pos):
        handle_reset()
    elif SOLVE_BUTTON.collidepoint(pos):
        handle_solve()
    else:
        selected = get_clicked_cell(pos)
        if selected:
            selected_cell = selected

def handle_keypress(event):
    global mistakes, game_over, final_time

    if not selected_cell or game_over:
        return

    row, col = selected_cell

    if board[row][col] != 0:
        return

    if event.unicode.isdigit() and event.unicode != "0":
        num = int(event.unicode)
        user_board[row][col] = num

        if not check_valid(user_board, row, col, num):
            invalid_cells.add((row, col))
            mistakes += 1
            if mistakes >= MAX_MISTAKES:
                game_over = True
                final_time = (pygame.time.get_ticks() - start_time) // 1000
        else:
            invalid_cells.discard((row, col))

    elif event.key == pygame.K_BACKSPACE:
        user_board[row][col] = 0
        invalid_cells.discard((row, col))

# Main Loop
def main():
    global selected_cell
    run = True

    while run:
        clock.tick(60) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit the game
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                handle_keypress(event)
                
        draw_window()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
