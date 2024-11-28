import pygame
import sys
import random
import time
import os
from pygame import mixer

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game colors
colors = [
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (128, 0, 128),    # Purple
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (255, 255, 255),  # White
]

# Function to get the proper path for assets
def resource_path(relative_path):
    """Get the absolute path to a resource, works for both development and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")  # Current directory if not bundled
    return os.path.join(base_path, relative_path)

# Game assets
background = pygame.image.load(resource_path('images/fillMasterBG.png'))
icon = pygame.image.load(resource_path('images/fillMasterIcon.png'))
button_image = pygame.image.load(resource_path('images/main_button.PNG'))
button_image = pygame.transform.scale(button_image, (360, 50))
small_button_image = pygame.transform.scale(button_image, (80, 40))

pygame.display.set_caption("Fill Master")
pygame.display.set_icon(icon)

# Game state variables
current_screen = "home"
board_size = 6
moves_left = 20
board = []
level = 1
cell_size = 50
challenge_mode = False
challenge_timer = 0
level_selection_page = 0

#background music
mixer.music.load(resource_path('bgm/bgm.mp3'))
mixer.music.play(-1)
mixer.music.set_volume(0.9)

win_bgm_played = False  
lose_bgm_played = False  

buttonClick_sound = mixer.Sound(resource_path('bgm/click.mp3'))


#helper function for fonts
def get_font(size):
    return pygame.font.Font(resource_path('images/font.ttf'), size)

#helper functions to set the current screen
def set_screen(screen_name):
    global current_screen
    current_screen = screen_name


#flood fill algorithm to change the board color, using DFS
def flood_fill(x, y, target_color, new_color):
    #checking if the current position are out of bounds
    #if the current position is outside the grid, return
    if x < 0 or x >= board_size or y < 0 or y >= board_size:
        return
    
    #checking if the current cell's color is the target color or if the cell has already a new color
    if board[x][y] != target_color or board[x][y] == new_color:
        return
    
    board[x][y] = new_color #change the current cell's color to the new one
    #recursive call for the 4 adjacent cells
    flood_fill(x + 1, y, target_color, new_color) #check right
    flood_fill(x - 1, y, target_color, new_color) #check left
    flood_fill(x, y + 1, target_color, new_color) #check down
    flood_fill(x, y - 1, target_color, new_color) #check up


#generate random colors for the board
def generate_board():
    global board, cell_size
    cell_size = min(400// board_size , 50)
    board = [[random.choice(colors) for _ in range(board_size)] for _ in range (board_size)]


# Reset the game
def reset_game(size, new_moves, time_limit=None):
    global board_size, moves_left, board, challenge_mode, challenge_timer, cell_size, current_board, current_timeLimit, win_bgm_played, lose_bgm_played
    board_size = min(size, 20)  # Update board size
    moves_left = new_moves  # Reset moves left
    challenge_mode = time_limit is not None  # Check if the game is in challenge mode
    challenge_timer = time.time() + time_limit if time_limit else 0  # Reset timer if Challenge Mode
    current_timeLimit = time_limit
    # Dynamically adjust the cell size based on the board size
    cell_size = min(400 // board_size, 50)
    win_bgm_played = False  # Initialized flag for the bgm if player wins
    lose_bgm_played = False #initialize flag for the bgm if player lose the game

    generate_board()  # Generate a new random board

    if not challenge_mode:  # no timer for classic mode
        challenge_timer = 0



def check_win():
    #check if all the cells in the board are the same color
    target_color = board[0][0]
    return all(cell == target_color for row in board for cell in row)


def go_to_home():
    global current_screen, board_size, moves_left, board, win_bgm_played, lose_bgm_played
    current_screen = "home"
    board_size = 6  # Default board size
    moves_left = 20  # Default moves
    board = []  # Clear the board
    win_bgm_played = False #update the flag for the bgm (win)
    lose_bgm_played = False #update the flag for the bgn (lose)

#this screen will pop up if the player wins
def win_screen():
    global win_bgm_played  # Access the flag
    
    if not win_bgm_played:  # Check if the music hasn't played yet
        win_bgm = mixer.Sound(resource_path('bgm/win sound.mp3'))
        win_bgm.play()
        win_bgm_played = True 
    
    screen.fill((62, 65, 120)) 
    win_text = get_font(40).render("YOU WIN!", True, WHITE)
    win_text_rect = win_text.get_rect(center=(400, 100))
    screen.blit(win_text, win_text_rect)

    if challenge_mode: 
        create_button(
            button_image,
            "Again",
            (400, 290),
            action=lambda: (
                reset_game(
                    board_size, 
                    15 if board_size == 6 else 
                    (20 if board_size == 8 else 
                    (30 if board_size == 15 else 15)),  # Fixed moves for Challenge Mode
                    current_timeLimit 
                ),
                set_screen("game")  
            )
        )
    else:  # if in the classic mode, show "next level" button
        if level < 25:  # Check if not at max level
            create_button(
                button_image,
                "Next Level",  
                (400, 290),
                action=lambda: (
                    set_screen("game"),  # Switch to the game screen
                    reset_game(
                        board_size + (1 if level <= 25 else 0), 
                        20 + (level - 1) ,  # Increase moves every level
                        None  # No time limit for Classic Mode
                    ),
                )
            )
        else:  # If all levels are completed
            end_text = get_font(14).render("Congratulations! You've completed all levels!", True, WHITE)
            end_text_rect = end_text.get_rect(center=(400, 290))
            screen.blit(end_text, end_text_rect)

    create_button(button_image, "Home", (400, 390), go_to_home)

#this screen will show if the player loses the game
def lose_screen():
    global lose_bgm_played  # Access the flag
    
    if not lose_bgm_played:  # Check if the music hasn't played yet
        lose_bgm = mixer.Sound(resource_path('bgm/game over sound.mp3'))
        lose_bgm.play()
        lose_bgm_played = True 

    screen.fill((191, 27, 27))
    lose_text = get_font(40).render("YOU LOSE!", True, WHITE)
    lose_text_rect = lose_text.get_rect(center=(400, 100))
    screen.blit(lose_text, lose_text_rect)

    # Button to retry the game
    create_button(
        button_image,
        "Retry",
        (400, 290),
        action=lambda: (
            reset_game(
                board_size,  # Keep the current board size
                20 + (level - 1)   if not challenge_mode else (
                    15 if board_size == 6 else (20 if board_size == 8 else 30)  # Reset moves for Challenge Mode
                ),
                30 if challenge_mode and board_size == 6 else (
                    50 if challenge_mode and board_size == 8 else (
                        80 if challenge_mode else None  # Time limit only for Challenge Mode
                    )
                )
            ) or set_screen("game")
        )
    )

    create_button(button_image, "Home", (400, 390), go_to_home)


#handle color changes during gameplay
def handle_color_change(color):
    global moves_left, current_screen, level
    
    target_color = board[0][0]
    if target_color != color:
        clickSound = mixer.Sound(resource_path('bgm/click sound for color buttons.mp3'))
        clickSound.play()
        flood_fill(0,0, target_color, color)
        moves_left -= 1

    if check_win():
        if current_screen == "game":
            level += 1
            set_screen("win")
    elif moves_left <= 0 or (challenge_mode and time.time() > challenge_timer):
        if current_screen == "game":
            set_screen("lose")


# choose board size for challenge mode
def board_size_screen():
    while current_screen == "board_size":
        screen.fill((40, 101, 120))
        title = get_font(30).render("Choose Board Size", True, WHITE)
        screen.blit(title, title.get_rect(center=(400, 100)))
        small_button = pygame.transform.scale(small_button_image, (80, 60))
        create_button(small_button, "<", (50, 50), lambda: set_screen("home"))
        create_button(button_image, "6x6", (400, 250), lambda: reset_game(6, 15, 30) or set_screen("game"))
        create_button(button_image, "8x8", (400, 350), lambda: reset_game(8, 20, 50) or set_screen("game"))
        create_button(button_image, "15x15", (400, 450), lambda: reset_game(15, 30, 80) or set_screen("game"))

        events()
        pygame.display.update()

#renders the gameplay screen
def render_game_screen():
    global moves_left

    while current_screen == "game":
        screen.fill((40, 101, 120))

        # Dynamically calculate the starting position for centering
        board_start_x = (SCREEN_WIDTH - cell_size * board_size) // 2
        board_start_y = (SCREEN_HEIGHT - cell_size * board_size) // 2 - 50

        # Draw the grid
        for x in range(board_size):
            for y in range(board_size):
                rect = pygame.Rect(board_start_x + y * cell_size, board_start_y + x * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, board[x][y], rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        #moves left text
        moves_text = get_font(20).render(f"Moves Left: {moves_left}", True, WHITE)
        screen.blit(moves_text, (250, 30))

        # Challenge mode timer 
        if challenge_mode:
            time_left = max(0, int(challenge_timer - time.time()))  # Calculate remaining time
            timer_text = get_font(20).render(f"Time Left: {time_left}s", True, WHITE)
            screen.blit(timer_text, (240, 550))
            if time_left <= 0:
                set_screen("lose")  # current screen will be lose screen if time runs out

        #color buttons
        button_width = 60
        button_spacing = 10
        buttons_start_x = (SCREEN_WIDTH - (len(colors) * button_width + (len(colors) - 1) * button_spacing)) // 2
        buttons_start_y = board_start_y + cell_size * board_size + 20
        #enumerated through the list of colors and draws them as reactangle buttons at the bottom of the grid
        for idx, color in enumerate(colors):
            button_rect = pygame.Rect(buttons_start_x + idx * (button_width + button_spacing), buttons_start_y, button_width, button_width)
            pygame.draw.rect(screen, pygame.Color(color), button_rect)
            if pygame.mouse.get_pressed()[0] and button_rect.collidepoint(pygame.mouse.get_pos()):
                handle_color_change(color)
                pygame.time.delay(200) #delay after click to prevent misclicks

        small_button = pygame.transform.scale(small_button_image, (60, 50))
        create_button(small_button, "<", (50, 50), lambda: set_screen("home"))
        # Info button to show game mechanics
        create_button(small_button, "?", (SCREEN_WIDTH - 50, 50), lambda: set_screen("modal"))


        events()
        pygame.display.update()

#this if for the "?" button during gameplay
def render_modal():
    screen.fill((40, 101, 120)) 
    pygame.draw.rect(screen, WHITE, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), border_radius=20)
    title = get_font(30).render("How to Play", True, BLACK)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

    # Mechanics Text
    mechanics = [
        "1. Fill the entire board with a single color.",
        "2. Click a color from the buttons on the \n   bottom to start flooding.",
        "3. Flooding will start from the top-left corner",
        "4. Classic Mode: Progress through \n   levels with larger grids.",
        "   Challenge Mode: Choose a board size \n   and beat the timer.",
        "5. Focus on colors that flood the largest areas.",
        "6. Win: Fill the board with one color \n   before moves/time run out.",
    ]


    # Display mechanics text
    y_offset = 200
    for line in mechanics:
        for subline in line.split("\n"):
            text = get_font(10).render(subline, True, BLACK)
            screen.blit(text, (150, y_offset))
            y_offset += 20

    small_button = pygame.transform.scale(button_image, (150, 50))
    create_button(small_button, "Close", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150), lambda: set_screen("game"))

    # Handling the event to close the modal and return to the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if SCREEN_WIDTH // 2 - 90 <= mouse_pos[0] <= SCREEN_WIDTH // 2 + 90 and SCREEN_HEIGHT - 130 <= mouse_pos[1] <= SCREEN_HEIGHT - 70:
                set_screen("game") 

    pygame.display.update()


#creating buttons
def create_button(image, text, pos, action=None, text_color=WHITE, hover_color=BLACK):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Create a new rect for this button based on the position
    rect = pygame.Rect(pos[0] - image.get_width() // 2, pos[1] - image.get_height() // 2, image.get_width(), image.get_height())

    is_hovered = rect.collidepoint(mouse)
    font = get_font(20)

    # hover effects
    if is_hovered:
        text_surface = font.render(text, True, hover_color)
    else:
        text_surface = font.render(text, True, text_color)

    # Draw the button and text
    screen.blit(image, rect.topleft)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    # Handle button click
    if is_hovered and click[0] == 1 and action is not None:
        buttonClick_sound.play()
        buttonClick_sound.set_volume(0.5)
        pygame.time.delay(200)
        action()

def start_classic_level(selected_level):
    global level
    level = selected_level
    moves = 20 + (level -1) #increases the moves by 1 every level
    grid_size = min(6 + (level - 1) // 2, 20) #increments the grid size every 2 levels
    reset_game(grid_size, moves, None)
    set_screen("game")

 #this is for level page navigation   
def set_page(offset):
    global level_selection_page
    level_selection_page = max(0, level_selection_page + offset)

#level selection page
def level_select_screen():
    global level_selection_page

    while current_screen == "level_select":
        screen.fill((62, 65, 120))
        title = get_font(40).render("Levels", True, WHITE)
        screen.blit(title, title.get_rect(center=(400, 50)))

        # Display up to 25 levels, paginated in groups of 9
        max_levels = 25
        levels_per_page = 9
        start_level = level_selection_page * levels_per_page + 1
        end_level = min(start_level + levels_per_page - 1, max_levels)

        # Buttons to select levels
        for i, level_num in enumerate(range(start_level, end_level + 1)):
            x = 180 + (i % 3) * 220
            y = 180 + (i // 3) * 120
            small_button = pygame.transform.scale(small_button_image, (80, 60))
            create_button(
                small_button,
                str(level_num),
                (x, y),
                lambda l=level_num: start_classic_level(l)
            )

        # Navigation buttons
        if level_selection_page > 0:  # Show "←" only if not on the first page
            create_button(small_button, "←", (100, 550), lambda: set_page(-1))
        if end_level < max_levels:  # Show "→" only if more levels are available
            create_button(small_button, "→", (700, 550), lambda: set_page(1))
        create_button(small_button, "<", (50, 50), lambda: set_screen("home"))

        events()
        pygame.display.update()


def main_menu():
    # Render the main menu
    screen.blit(background, (0, 0))

    # Title text
    MENU_TEXT = get_font(41).render("FILL MASTER", True, "White")
    MENU_RECT = MENU_TEXT.get_rect(center=(400, 100))

    # rectangle for the title
    rect_width = MENU_TEXT.get_width() + 400
    rect_height = MENU_TEXT.get_height() + 60
    rect_x = MENU_RECT.left - 200
    rect_y = MENU_RECT.top - 30
    pygame.draw.rect(screen, "black", (rect_x, rect_y, rect_width, rect_height))

    screen.blit(MENU_TEXT, MENU_RECT)

    # buttons to navigate the app
    create_button(button_image, "Classic", (400, 320), lambda: set_screen("level_select"))
    create_button(button_image, "Challenge Mode", (400, 400), lambda: set_screen("board_size"))
    create_button(button_image, "Quit", (400, 480), sys.exit)


#event handling
def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


#game loop
def game_loop():
    global current_screen

    while True:
        #render the correct current screen
        if current_screen == "home":
            main_menu()
        elif current_screen == "board_size":
            board_size_screen()
        elif current_screen == "level_select":
            level_select_screen()
        elif current_screen == "game":
            render_game_screen()
        elif current_screen == "win":
            win_screen()
        elif current_screen == "lose":
            lose_screen()
        elif current_screen == "modal":
            render_modal()

        events()
        pygame.display.update()
game_loop()