# Sudoku Game with Difficulty Menu
import pygame
import sys
import random

# Initialization
pygame.init()
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 9
CELL_SIZE = (WIDTH - 60) // GRID_SIZE
MAX_MISTAKES = 5

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
DARK_BLUE = (0, 0, 200)
GRAY = (120, 120, 120)

# Grid Layout
LEFT_PADDING = 30
TOP_PADDING = 45
GRID_WIDTH = WIDTH - 2 * LEFT_PADDING
GRID_HEIGHT = GRID_WIDTH

# Fonts & Buttons
FONT_MAIN = pygame.font.SysFont("comicsans", 40)
FONT_TITLE = pygame.font.SysFont("comicsans", 60)
FONT_SMALL = pygame.font.SysFont("Segoe UI Emoji", 24)

RESET_BUTTON = pygame.Rect(LEFT_PADDING, HEIGHT - 50, 100, 40)
SOLVE_BUTTON = pygame.Rect(WIDTH - LEFT_PADDING - 100, HEIGHT - 50, 100, 40)
MENU_BUTTON = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 50, 100, 40)
    
# Setup Game Window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")
clock = pygame.time.Clock()

# Game State
board = []
user_board = []
selected_cell = None
invalid_cells = set()
mistakes = 0
game_over = False
sol_check = False
final_time = 0
start_time = 0
in_main_menu = True
hint_cells = set()  # cells revealed via hint
hints_used = 0

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

def fill_board(bd):
    """Fill the board completely using backtracking."""
    empty = find_empty(bd)
    if not empty:
        return True
        
    row, col = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if check_valid(bd, row, col, num):
            bd[row][col] = num
            if fill_board(bd):
                return True
            bd[row][col] = 0
    return False

def remove_numbers(bd, clues):
    """Remove numbers to create a puzzle with the specified number of clues."""
    attempts = 81 - clues
    while attempts > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if bd[r][c] != 0:
            backup = bd[r][c]
            bd[r][c] = 0

            # Copy and solve to ensure it's still solvable
            copy = [row[:] for row in bd]
            if not solve(copy):
                bd[r][c] = backup # revert if unsolvable
            else:
                attempts -= 1

def generate_board(difficulty):
    """Generate a new board based on difficulty."""
    full = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    fill_board(full)

    difficulty_levels = {
        "easy": random.randint(36, 40),
        "medium": random.randint(32, 35),
        "hard": random.randint(28, 31),
    }

    board_copy = [row[:] for row in full]
    remove_numbers(board_copy, difficulty_levels[difficulty])
    return board_copy

# Drawing Functions
def draw_grid():
    for i in range(GRID_SIZE + 1):
        line_width = 4 if i % 3 == 0 else 1
        x = LEFT_PADDING + i * CELL_SIZE
        y = TOP_PADDING + i * CELL_SIZE
        pygame.draw.line(WIN, BLACK, (x, TOP_PADDING), (x, TOP_PADDING + GRID_HEIGHT), line_width)
        pygame.draw.line(WIN, BLACK, (LEFT_PADDING, y), (LEFT_PADDING + GRID_WIDTH, y), line_width)

def draw_numbers():
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
                
                text = FONT_MAIN.render(str(val), True, color)
                x = LEFT_PADDING + j * CELL_SIZE + 20
                y = TOP_PADDING + i * CELL_SIZE
                WIN.blit(text, (x, y))

def draw_selection():
    """Highlight the selected cell's row, column, and subgrid."""
    if not selected_cell:
        return

    row, col = selected_cell

    # Create a transparent surface
    hl_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
    hl_surf.set_alpha(60)
    hl_surf.fill(LIGHT_BLUE)

    # Highlight row
    for j in range(GRID_SIZE):
        x = LEFT_PADDING + j * CELL_SIZE
        y = TOP_PADDING + row * CELL_SIZE
        WIN.blit(hl_surf, (x, y))

    # Highlight column
    for i in range(GRID_SIZE):
        if i == row:
            continue  # Already highlighted in row
        x = LEFT_PADDING + col * CELL_SIZE
        y = TOP_PADDING + i * CELL_SIZE
        WIN.blit(hl_surf, (x, y))

    # Highlight 3x3 box
    box_start_row = (row // 3) * 3
    box_start_col = (col // 3) * 3
    for i in range(box_start_row, box_start_row + 3):
        for j in range(box_start_col, box_start_col + 3):
            if i == row or j == col:
                continue  # Already highlighted
            x = LEFT_PADDING + j * CELL_SIZE
            y = TOP_PADDING + i * CELL_SIZE
            WIN.blit(hl_surf, (x, y))

    # Draw a strong border around the selected cell
    x = LEFT_PADDING + col * CELL_SIZE
    y = TOP_PADDING + row * CELL_SIZE
    pygame.draw.rect(WIN, LIGHT_BLUE, (x, y, CELL_SIZE, CELL_SIZE), 3)

def draw_buttons(): 
    pygame.draw.rect(WIN, GREEN, RESET_BUTTON)
    pygame.draw.rect(WIN, DARK_BLUE, SOLVE_BUTTON)
    pygame.draw.rect(WIN, GRAY, MENU_BUTTON)
    
    WIN.blit(FONT_SMALL.render("Reset", True, WHITE), (RESET_BUTTON.x + 20, RESET_BUTTON.y + 10))
    WIN.blit(FONT_SMALL.render("Solve", True, WHITE), (SOLVE_BUTTON.x + 20, SOLVE_BUTTON.y + 10))
    WIN.blit(FONT_SMALL.render("Menu", True, WHITE), (MENU_BUTTON.x + 20, MENU_BUTTON.y + 10))

def draw_stats():
    # Timer
    elapsed = (pygame.time.get_ticks() - start_time) // 1000 if not sol_check and not game_over else final_time
    mins, secs = divmod(elapsed, 60)
    WIN.blit(FONT_SMALL.render(f"\u23F1  {mins:02}:{secs:02}", True, BLACK), (LEFT_PADDING, 10))

    # Hints
    BULB_BUTTON = pygame.Rect(WIDTH - 170, 10, 32, 32)
    WIN.blit(FONT_SMALL.render(f"💡", True, BLACK), (BULB_BUTTON.x, BULB_BUTTON.y))
    
    # Mistakes
    WIN.blit(FONT_SMALL.render(f"\u274C {mistakes}/{MAX_MISTAKES}", True, RED), (WIDTH - 110, 10))

def draw_main_menu():
    WIN.fill(WHITE)
    title = FONT_TITLE.render("Sudoku", True, BLACK)
    WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    easy_button = pygame.Rect(WIDTH // 2 - 100, 220, 200, 60)
    med_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 60)
    hard_button = pygame.Rect(WIDTH // 2 - 100, 380, 200, 60)

    pygame.draw.rect(WIN, LIGHT_BLUE, easy_button)
    pygame.draw.rect(WIN, LIGHT_BLUE, med_button)
    pygame.draw.rect(WIN, LIGHT_BLUE, hard_button)

    WIN.blit(FONT_MAIN.render("Easy", True, WHITE), (easy_button.x + 55, easy_button.y))
    WIN.blit(FONT_MAIN.render("Medium", True, WHITE), (med_button.x + 30, med_button.y))
    WIN.blit(FONT_MAIN.render("Hard", True, WHITE), (hard_button.x + 55, hard_button.y))

    pygame.display.update()
    return easy_button, med_button, hard_button

def draw_window():
    WIN.fill(WHITE)
    draw_stats()
    draw_grid()
    draw_selection()
    draw_numbers()
    draw_buttons()
    
    if game_over:
        overlay = pygame.Surface((GRID_WIDTH + 8, GRID_HEIGHT + 8))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        WIN.blit(overlay, (LEFT_PADDING - 2, TOP_PADDING - 2))
        msg = FONT_TITLE.render("Game Over!", True, RED)
        WIN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 25))
        
    pygame.display.update()

# Game Actions
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

def start_new_game(difficulty):
    global board, user_board, selected_cell, mistakes, game_over, sol_check, final_time, start_time

    board = generate_board(difficulty)
    user_board = [row[:] for row in board]
    selected_cell = None
    invalid_cells.clear()
    mistakes = 0
    game_over = False
    sol_check = False
    final_time = 0
    start_time = pygame.time.get_ticks()

def return_to_menu():
    global board, user_board, selected_cell, mistakes, game_over, sol_check, final_time, in_main_menu

    # Reset game state
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    user_board = [row[:] for row in board]
    selected_cell = None
    invalid_cells.clear()
    mistakes = 0
    game_over = False
    sol_check = False
    final_time = 0
    in_main_menu = True
    
# Event Handlers
def handle_mouse_click(pos):
    global selected_cell
    
    if RESET_BUTTON.collidepoint(pos):
        handle_reset()
    elif SOLVE_BUTTON.collidepoint(pos):
        handle_solve()
    elif MENU_BUTTON.collidepoint(pos):
        return_to_menu()
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
    global in_main_menu
    run = True

    while run:
        clock.tick(60)

        if in_main_menu:
            easy_button, med_button, hard_button = draw_main_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_button.collidepoint(event.pos):
                        start_new_game("easy")
                        in_main_menu = False
                    elif med_button.collidepoint(event.pos):
                        start_new_game("medium")
                        in_main_menu = False
                    elif hard_button.collidepoint(event.pos):
                        start_new_game("hard")
                        in_main_menu = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    handle_keypress(event)

            draw_window()

    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()