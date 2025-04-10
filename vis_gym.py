import pygame
import sys
import time
import random
import os
from mdp_gym import CastleEscapeEnv

# Initialize dimensions
WIDTH, HEIGHT = 1000, 840
GRID_SIZE = 5
CELL_SIZE = min(WIDTH // GRID_SIZE, 120)
GAME_AREA_HEIGHT = CELL_SIZE * GRID_SIZE
CONSOLE_HEIGHT = HEIGHT - GAME_AREA_HEIGHT

# Enhanced color palette - rich medieval colors
WHITE = (255, 255, 255)
RED = (190, 30, 45)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # Forest green
BLUE = (65, 105, 225)  # Royal blue
GRAY = (105, 105, 105)
DARK_GRAY = (40, 40, 40)
YELLOW = (218, 165, 32)  # Golden
BROWN = (101, 67, 33)
STONE_GRAY = (120, 124, 129)
CONSOLE_BG = (30, 25, 40)  # Deep purple-ish background
TEXT_COLOR = (230, 220, 180)  # Parchment color for text
GOLD = (212, 175, 55)
PARCHMENT = (255, 252, 220)

# Create directory for assets if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Define file paths for images
IMGFILEPATH = {
    "stone_floor": "assets/stone_floor.png",
    "goal_room": "assets/goal_room.png",
    "player": "assets/player.png",
    "guard": "assets/guard.png",
    "wall_h": "assets/wall_h.png",
    "wall_v": "assets/wall_v.png",
    "health_full": "assets/health_full.png",
    "health_injured": "assets/health_injured.png",
    "health_critical": "assets/health_critical.png",
    "victory": "assets/victory.png",
    "defeat": "assets/defeat.png",
    "background": "assets/background.png",
    "scroll": "assets/scroll.png",
    "health_bar": "assets/health_bar.png",
    "controls_panel": "assets/controls_panel.png"
}

# Setup display
screen = None
game_ended = False
action_results = [None, None, None, None, None]
fps = 60
sleeptime = 0.1
clock = None
animation_frame = 0  # For animated elements

# Initialize MDP game
game = CastleEscapeEnv()

# Load or create images with enhanced visuals
def load_images():
    images = {}
    
    # Generate stone floor texture with more detail
    floor = pygame.Surface((CELL_SIZE, CELL_SIZE))
    floor.fill(STONE_GRAY)
    
    # Add stone patterns
    for _ in range(15):
        x, y = random.randint(0, CELL_SIZE-1), random.randint(0, CELL_SIZE-1)
        size = random.randint(10, 20)
        color = (random.randint(110, 150), random.randint(110, 150), random.randint(110, 150))
        pygame.draw.rect(floor, color, (x, y, size, size))
    
    # Add cracks and details
    for _ in range(8):
        start_x, start_y = random.randint(0, CELL_SIZE-1), random.randint(0, CELL_SIZE-1)
        end_x, end_y = random.randint(0, CELL_SIZE-1), random.randint(0, CELL_SIZE-1)
        pygame.draw.line(floor, (80, 80, 80), (start_x, start_y), (end_x, end_y), 1)
    
    pygame.image.save(floor, IMGFILEPATH["stone_floor"])
    images["stone_floor"] = floor
    
    # Generate goal room texture - treasure chamber
    goal = pygame.Surface((CELL_SIZE, CELL_SIZE))
    
    # Golden gradient background
    for y in range(CELL_SIZE):
        gold_shade = (212, 175 - y//3, 55 - y//6)
        pygame.draw.line(goal, gold_shade, (0, y), (CELL_SIZE, y))
    
    # Add gold coins/treasure
    for _ in range(20):
        x, y = random.randint(5, CELL_SIZE-6), random.randint(5, CELL_SIZE-6)
        size = random.randint(3, 7)
        pygame.draw.circle(goal, (255, 215, 0), (x, y), size)  # Gold coins
        pygame.draw.circle(goal, (255, 255, 220), (x-1, y-1), size//3)  # Shine effect
    
    # Add EXIT text with fancy styling
    font_size = max(18, min(36, CELL_SIZE // 3))
    try:
        font = pygame.font.SysFont("medievalsharp", font_size, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
    
    # Create text with shadow for depth
    text_shadow = font.render("EXIT", True, (100, 70, 0))
    text = font.render("EXIT", True, (255, 255, 220))
    
    # Position text with shadow
    goal.blit(text_shadow, (CELL_SIZE//2 - text.get_width()//2 + 2, 
                          CELL_SIZE//2 - text.get_height()//2 + 2))
    goal.blit(text, (CELL_SIZE//2 - text.get_width()//2, 
                   CELL_SIZE//2 - text.get_height()//2))
    
    pygame.image.save(goal, IMGFILEPATH["goal_room"])
    images["goal_room"] = goal
    
    # Enhanced player sprite - knight with armor and sword
    player_size = max(CELL_SIZE//2, 30)
    player = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    
    # Body (armor)
    pygame.draw.circle(player, (50, 50, 150), (player_size//2, player_size//2), player_size//2 - 2)
    
    # Helmet
    helmet_width = player_size * 3//4
    helmet_height = player_size//3
    helmet_rect = pygame.Rect(
        player_size//2 - helmet_width//2, 
        player_size//4 - helmet_height//2,
        helmet_width, 
        helmet_height
    )
    pygame.draw.ellipse(player, (100, 100, 200), helmet_rect)
    
    # Face opening
    face_width = helmet_width // 2
    face_height = helmet_height // 2
    face_rect = pygame.Rect(
        player_size//2 - face_width//2,
        player_size//4 - face_height//2,
        face_width,
        face_height
    )
    pygame.draw.ellipse(player, (0, 0, 0), face_rect)
    
    # Sword
    sword_length = player_size * 3//4
    hilt_width = player_size//6
    
    # Blade
    pygame.draw.line(player, (200, 200, 220), 
                    (player_size - player_size//4, player_size//2), 
                    (player_size - player_size//4 + sword_length//2, player_size//2 - sword_length//2), 
                    max(3, player_size//8))
    
    # Hilt
    pygame.draw.line(player, (160, 120, 40), 
                    (player_size - player_size//4, player_size//2), 
                    (player_size - player_size//4, player_size//2 + hilt_width), 
                    max(4, player_size//6))
    
    # Sword guard
    pygame.draw.line(player, (160, 120, 40), 
                    (player_size - player_size//4 - hilt_width//2, player_size//2), 
                    (player_size - player_size//4 + hilt_width//2, player_size//2), 
                    max(3, player_size//8))
    
    # Shield
    shield_x = player_size//4
    shield_y = player_size//2
    shield_size = player_size//3
    
    # Shield base
    pygame.draw.circle(player, (150, 30, 30), (shield_x, shield_y), shield_size)
    pygame.draw.circle(player, (180, 50, 50), (shield_x, shield_y), shield_size - 2)
    
    # Shield emblem (cross)
    pygame.draw.line(player, (220, 220, 220), 
                    (shield_x, shield_y - shield_size//2), 
                    (shield_x, shield_y + shield_size//2), 
                    max(2, shield_size//4))
    pygame.draw.line(player, (220, 220, 220), 
                    (shield_x - shield_size//2, shield_y), 
                    (shield_x + shield_size//2, shield_y), 
                    max(2, shield_size//4))
    
    pygame.image.save(player, IMGFILEPATH["player"])
    images["player"] = player
    
    # Enhanced guard sprite - medieval guard with spear
    guard_size = max(CELL_SIZE//2, 30)
    guard = pygame.Surface((guard_size, guard_size), pygame.SRCALPHA)
    
    # Body (armor)
    pygame.draw.rect(guard, (150, 30, 30), 
                    (guard_size//8, guard_size//3, 
                     3*guard_size//4, 2*guard_size//3),
                    border_radius=5)
    
    # Helmet
    helmet_height = guard_size//3
    pygame.draw.rect(guard, (120, 20, 20), 
                    (guard_size//8, guard_size//8, 
                     3*guard_size//4, helmet_height),
                    border_radius=3)
    
    # Helmet details
    pygame.draw.line(guard, (80, 10, 10), 
                    (guard_size//8, guard_size//8 + helmet_height//2), 
                    (guard_size//8 + 3*guard_size//4, guard_size//8 + helmet_height//2), 
                    2)
    
    # Face (dark opening in helmet)
    face_width = guard_size//4
    face_height = helmet_height//2
    face_x = guard_size//2 - face_width//2
    face_y = guard_size//8 + helmet_height//4
    pygame.draw.rect(guard, (40, 0, 0), 
                    (face_x, face_y, face_width, face_height),
                    border_radius=2)
    
    # Spear
    spear_length = guard_size * 3//4
    pygame.draw.line(guard, (120, 100, 80), 
                    (guard_size - guard_size//4, guard_size//3), 
                    (guard_size - guard_size//4 + spear_length//2, guard_size//3 - spear_length//2), 
                    max(2, guard_size//12))
    
    # Spear tip
    pygame.draw.polygon(guard, (180, 180, 180), [
        (guard_size - guard_size//4 + spear_length//2, guard_size//3 - spear_length//2 - guard_size//16),
        (guard_size - guard_size//4 + spear_length//2 + guard_size//10, guard_size//3 - spear_length//2),
        (guard_size - guard_size//4 + spear_length//2, guard_size//3 - spear_length//2 + guard_size//16)
    ])
    
    pygame.image.save(guard, IMGFILEPATH["guard"])
    images["guard"] = guard
    
    # Enhanced horizontal wall texture - stone wall with mortar
    wall_h = pygame.Surface((CELL_SIZE, max(6, CELL_SIZE//12)))
    
    # Base color
    wall_h.fill(BROWN)
    
    # Stone texture
    stones_per_wall = 4
    stone_width = CELL_SIZE // stones_per_wall
    wall_height = wall_h.get_height()
    
    for i in range(stones_per_wall):
        stone_color = (
            random.randint(90, 120),
            random.randint(60, 80),
            random.randint(30, 50)
        )
        pygame.draw.rect(wall_h, stone_color, 
                        (i * stone_width, 0, 
                         stone_width - 2, wall_height),
                        border_radius=1)
    
    pygame.image.save(wall_h, IMGFILEPATH["wall_h"])
    images["wall_h"] = wall_h
    
    # Enhanced vertical wall texture
    wall_v = pygame.Surface((max(6, CELL_SIZE//12), CELL_SIZE))
    
    # Base color
    wall_v.fill(BROWN)
    
    # Stone texture
    stones_per_wall = 4
    stone_height = CELL_SIZE // stones_per_wall
    wall_width = wall_v.get_width()
    
    for i in range(stones_per_wall):
        stone_color = (
            random.randint(90, 120),
            random.randint(60, 80),
            random.randint(30, 50)
        )
        pygame.draw.rect(wall_v, stone_color, 
                        (0, i * stone_height, 
                         wall_width, stone_height - 2),
                        border_radius=1)
    
    pygame.image.save(wall_v, IMGFILEPATH["wall_v"])
    images["wall_v"] = wall_v
    
    # Fancy health indicators
    health_height = min(30, CONSOLE_HEIGHT // 8)
    health_width = min(100, WIDTH // 6)
    
    # Health bar background frame
    health_bar = pygame.Surface((health_width + 10, health_height + 10))
    health_bar.fill((60, 40, 20))  # Wooden frame color
    pygame.draw.rect(health_bar, (40, 30, 15), 
                    (0, 0, health_width + 10, health_height + 10), 2)  # Frame border
    
    # Inside panel
    pygame.draw.rect(health_bar, (30, 20, 10), 
                    (5, 5, health_width, health_height))
    
    pygame.image.save(health_bar, IMGFILEPATH["health_bar"])
    images["health_bar"] = health_bar
    
    # Full health - vibrant green with pulse effect
    health_full = pygame.Surface((health_width, health_height))
    for x in range(health_width):
        # Gradient
        green_val = min(255, 50 + int(205 * (x / health_width)))
        for y in range(health_height):
            health_full.set_at((x, y), (0, green_val, 0))
    
    # Add heart symbols
    heart_size = min(8, health_height // 3)
    for i in range(3):
        x = health_width//4 * (i+1)
        y = health_height//2
        draw_heart(health_full, x, y, heart_size, (255, 255, 255))
    
    pygame.image.save(health_full, IMGFILEPATH["health_full"])
    images["health_full"] = health_full
    
    # Injured health - amber warning
    health_injured = pygame.Surface((health_width, health_height))
    for x in range(health_width):
        # Gradient
        amber_val = min(255, 100 + int(155 * (x / health_width)))
        for y in range(health_height):
            health_injured.set_at((x, y), (amber_val, amber_val//2, 0))
    
    # Add heart symbols (fewer)
    for i in range(2):
        x = health_width//3 * (i+1)
        y = health_height//2
        draw_heart(health_injured, x, y, heart_size, (255, 255, 255))
    
    pygame.image.save(health_injured, IMGFILEPATH["health_injured"])
    images["health_injured"] = health_injured
    
    # Critical health - alarming red pulse
    health_critical = pygame.Surface((health_width, health_height))
    for x in range(health_width):
        # Gradient effect
        red_val = min(255, 100 + int(155 * (x / health_width)))
        for y in range(health_height):
            health_critical.set_at((x, y), (red_val, 0, 0))
    
    # Add single heart
    x = health_width//2
    y = health_height//2
    draw_heart(health_critical, x, y, heart_size, (255, 255, 255))
    
    pygame.image.save(health_critical, IMGFILEPATH["health_critical"])
    images["health_critical"] = health_critical
    
    # Enhanced victory screen
    victory_width = min(400, WIDTH - 40)
    victory_height = min(200, GAME_AREA_HEIGHT // 2)
    
    victory = pygame.Surface((victory_width, victory_height))
    
    # Golden background with rays
    for y in range(victory_height):
        gold_tone = (min(255, 180 + y // 2), min(255, 130 + y // 3), 50)
        pygame.draw.line(victory, gold_tone, (0, y), (victory_width, y))
    
    # Add decorative border
    border_width = 10
    pygame.draw.rect(victory, (120, 100, 20), 
                    (0, 0, victory_width, victory_height), border_width)
    
    # Add corner decorations
    corner_size = 20
    for x, y in [(0, 0), (victory_width-corner_size, 0), 
                 (0, victory_height-corner_size), 
                 (victory_width-corner_size, victory_height-corner_size)]:
        pygame.draw.rect(victory, (150, 120, 30), 
                        (x, y, corner_size, corner_size))
        pygame.draw.rect(victory, (180, 150, 40), 
                        (x+2, y+2, corner_size-4, corner_size-4))
    
    # Victory text with medieval style
    try:
        font = pygame.font.SysFont("medievalsharp", 60, bold=True)
    except:
        font = pygame.font.Font(None, 60)
    
    # Text with shadow for depth
    text_shadow = font.render("VICTORY!", True, (100, 80, 0))
    text = font.render("VICTORY!", True, (255, 255, 220))
    
    # Crown above text
    crown_points = [
        (victory_width//2, victory_height//4),
        (victory_width//2 - 40, victory_height//3),
        (victory_width//2 - 30, victory_height//4),
        (victory_width//2 - 15, victory_height//3),
        (victory_width//2, victory_height//4),
        (victory_width//2 + 15, victory_height//3),
        (victory_width//2 + 30, victory_height//4),
        (victory_width//2 + 40, victory_height//3),
    ]
    pygame.draw.polygon(victory, (255, 215, 0), crown_points)
    
    # Add jewels to crown
    jewel_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
    jewel_positions = [
        (victory_width//2 - 30, victory_height//4 + 5),
        (victory_width//2 - 15, victory_height//4 + 5),
        (victory_width//2, victory_height//4 + 5),
        (victory_width//2 + 15, victory_height//4 + 5),
        (victory_width//2 + 30, victory_height//4 + 5)
    ]
    
    for i, pos in enumerate(jewel_positions):
        pygame.draw.circle(victory, jewel_colors[i % len(jewel_colors)], pos, 5)
    
    # Position text with shadow
    victory.blit(text_shadow, (victory_width//2 - text.get_width()//2 + 3, 
                           victory_height//2 - text.get_height()//2 + 3))
    victory.blit(text, (victory_width//2 - text.get_width()//2, 
                    victory_height//2 - text.get_height()//2))
    
    # Add "FREEDOM ACHIEVED" subtitle
    try:
        subtitle_font = pygame.font.SysFont("medievalsharp", 24)
    except:
        subtitle_font = pygame.font.Font(None, 24)
    
    subtitle = subtitle_font.render("FREEDOM ACHIEVED", True, (255, 255, 220))
    victory.blit(subtitle, (victory_width//2 - subtitle.get_width()//2, 
                          victory_height - subtitle.get_height() - 20))
    
    pygame.image.save(victory, IMGFILEPATH["victory"])
    images["victory"] = victory
    
    # Enhanced defeat screen
    defeat = pygame.Surface((victory_width, victory_height))
    
    # Dark red background with smoke-like effect
    for y in range(victory_height):
        for x in range(victory_width):
            noise = random.randint(-10, 10)
            red_val = max(60, min(150, 100 + noise))
            pygame.draw.line(defeat, (red_val, 10, 10), (x, y), (x, y))
    
    # Add decorative border
    border_width = 10
    pygame.draw.rect(defeat, (80, 0, 0), 
                    (0, 0, victory_width, victory_height), border_width)
    
    # Add broken chains in corners
    chain_positions = [(20, 20), (victory_width-40, 20), 
                      (20, victory_height-40), 
                      (victory_width-40, victory_height-40)]
    
    for x, y in chain_positions:
        # Draw broken chain links
        pygame.draw.circle(defeat, (100, 100, 100), (x, y), 8, 2)
        pygame.draw.circle(defeat, (100, 100, 100), (x+15, y+10), 8, 2)
        pygame.draw.line(defeat, (150, 150, 150), (x+4, y+4), (x+11, y+6), 2)
    
    # Defeat text with medieval style
    try:
        font = pygame.font.SysFont("medievalsharp", 60, bold=True)
    except:
        font = pygame.font.Font(None, 60)
    
    # Text with shadow for depth
    text_shadow = font.render("DEFEATED!", True, (20, 0, 0))
    text = font.render("DEFEATED!", True, (200, 0, 0))
    
    # Skull above text
    skull_center = (victory_width//2, victory_height//4)
    skull_size = 30
    
    # Skull base
    pygame.draw.circle(defeat, (200, 200, 200), skull_center, skull_size)
    
    # Eye sockets
    eye_offset = 10
    eye_size = 8
    pygame.draw.circle(defeat, (0, 0, 0), 
                     (skull_center[0] - eye_offset, skull_center[1] - 5), eye_size)
    pygame.draw.circle(defeat, (0, 0, 0), 
                     (skull_center[0] + eye_offset, skull_center[1] - 5), eye_size)
    
    # Nose
    pygame.draw.polygon(defeat, (0, 0, 0), [
        (skull_center[0], skull_center[1]),
        (skull_center[0] - 5, skull_center[1] + 10),
        (skull_center[0] + 5, skull_center[1] + 10)
    ])
    
    # Teeth
    teeth_width = 24
    teeth_height = 8
    teeth_top = skull_center[1] + 15
    teeth_left = skull_center[0] - teeth_width//2
    
    for i in range(4):
        tooth_x = teeth_left + i * (teeth_width//4)
        pygame.draw.rect(defeat, (220, 220, 220), 
                        (tooth_x, teeth_top, teeth_width//4 - 1, teeth_height))
        pygame.draw.rect(defeat, (0, 0, 0), 
                        (tooth_x, teeth_top, teeth_width//4 - 1, teeth_height), 1)
    
    # Position text with shadow
    defeat.blit(text_shadow, (victory_width//2 - text.get_width()//2 + 3, 
                           victory_height//2 - text.get_height()//2 + 3))
    defeat.blit(text, (victory_width//2 - text.get_width()//2, 
                    victory_height//2 - text.get_height()//2))
    
    # Add "THE DUNGEON CLAIMS ANOTHER" subtitle
    try:
        subtitle_font = pygame.font.SysFont("medievalsharp", 24)
    except:
        subtitle_font = pygame.font.Font(None, 24)
    
    subtitle = subtitle_font.render("THE DUNGEON CLAIMS ANOTHER", True, (200, 0, 0))
    defeat.blit(subtitle, (victory_width//2 - subtitle.get_width()//2, 
                          victory_height - subtitle.get_height() - 20))
    
    pygame.image.save(defeat, IMGFILEPATH["defeat"])
    images["defeat"] = defeat
    
    # Create background with castle stone pattern
    background = pygame.Surface((WIDTH, HEIGHT))
    
    # Fill with dark stone pattern
    background.fill(DARK_GRAY)
    
    # Add stone-like texture
    for _ in range(500):
        x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        size = random.randint(3, 8)
        color_var = random.randint(-20, 20)
        color = (min(255, max(0, 40 + color_var)), 
                min(255, max(0, 40 + color_var)), 
                min(255, max(0, 45 + color_var)))
        pygame.draw.rect(background, color, (x, y, size, size))
    
    # Add some cracks
    for _ in range(20):
        start_x, start_y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        length = random.randint(20, 100)
        angle = random.random() * 6.28
        end_x = start_x + int(length * math.cos(angle))
        end_y = start_y + int(length * math.sin(angle))
        pygame.draw.line(background, (30, 30, 30), (start_x, start_y), (end_x, end_y), 2)
    
    pygame.image.save(background, IMGFILEPATH["background"])
    images["background"] = background
    
    # Torch animation removed as requested
    
    # Create fancy controls panel (stone tablet)
    controls_width = WIDTH // 3
    controls_height = CONSOLE_HEIGHT // 2
    
    controls_panel = pygame.Surface((controls_width, controls_height))
    
    # Stone tablet gradient
    for y in range(controls_height):
        stone_color = (
            min(130, 100 + y//8),
            min(130, 100 + y//10),
            min(130, 90 + y//12)
        )
        pygame.draw.line(controls_panel, stone_color, (0, y), (controls_width, y))
    
    # Add stone texture
    for _ in range(100):
        x, y = random.randint(0, controls_width-1), random.randint(0, controls_height-1)
        size = random.randint(2, 5)
        color_var = random.randint(-15, 15)
        color = (
            min(255, max(0, 110 + color_var)),
            min(255, max(0, 110 + color_var)),
            min(255, max(0, 100 + color_var))
        )
        pygame.draw.rect(controls_panel, color, (x, y, size, size))
    
    # Add tablet border with chisel effect
    border_width = 5
    inner_border = 2
    
    # Outer border (shadow)
    pygame.draw.rect(controls_panel, (80, 80, 70), 
                    (0, 0, controls_width, controls_height), border_width)
    
    # Inner border (highlight)
    pygame.draw.rect(controls_panel, (140, 140, 130), 
                    (border_width-inner_border, border_width-inner_border, 
                     controls_width-2*(border_width-inner_border), 
                     controls_height-2*(border_width-inner_border)), 
                    inner_border)
    
    # Add some "carved" marks
    for _ in range(5):
        x = random.randint(border_width, controls_width-border_width)
        y = random.randint(border_width, controls_height-border_width)
        length = random.randint(5, 15)
        angle = random.random() * 6.28
        end_x = x + int(length * math.cos(angle))
        end_y = y + int(length * math.sin(angle))
        pygame.draw.line(controls_panel, (80, 80, 70), (x, y), (end_x, end_y), 1)
    
    pygame.image.save(controls_panel, IMGFILEPATH["controls_panel"])
    images["controls_panel"] = controls_panel
    
    # Create scroll for console
    scroll_width = WIDTH - 20
    scroll_height = CONSOLE_HEIGHT - 50
    
    scroll = pygame.Surface((scroll_width, scroll_height))
    
    # Parchment background color
    scroll.fill(PARCHMENT)
    
    # Add parchment texture
    for _ in range(200):
        x, y = random.randint(0, scroll_width-1), random.randint(0, scroll_height-1)
        size = random.randint(1, 3)
        color_var = random.randint(-10, 10)
        color = (
            min(255, max(220, 240 + color_var)),
            min(255, max(220, 237 + color_var)),
            min(255, max(200, 210 + color_var))
        )
        pygame.draw.rect(scroll, color, (x, y, size, size))
    
    # Add some "age" spots
    for _ in range(30):
        x, y = random.randint(0, scroll_width-1), random.randint(0, scroll_height-1)
        size = random.randint(3, 8)
        color = (220 - random.randint(0, 40), 
                210 - random.randint(0, 50), 
                180 - random.randint(0, 30))
        pygame.draw.circle(scroll, color, (x, y), size)
    
    # Add scroll edges (rolled)
    edge_width = 15
    
    # Left scroll edge (darker)
    for x in range(edge_width):
        shadow = int(100 * (1 - x/edge_width))
        color = (max(180, 235 - shadow), max(180, 232 - shadow), max(160, 205 - shadow))
        pygame.draw.line(scroll, color, (x, 0), (x, scroll_height))
    
    # Right scroll edge
    for x in range(edge_width):
        x_pos = scroll_width - edge_width + x
        shadow = int(50 * (x/edge_width))
        color = (max(180, 235 - shadow), max(180, 232 - shadow), max(160, 205 - shadow))
        pygame.draw.line(scroll, color, (x_pos, 0), (x_pos, scroll_height))
    
    # Add scroll shadows
    for y in range(scroll_height):
        shadow_size = min(5, abs(y - scroll_height//2) // 20)
        left_color = (max(180, 235 - shadow_size*10), 
                     max(180, 232 - shadow_size*10), 
                     max(160, 205 - shadow_size*10))
        pygame.draw.line(scroll, left_color, (0, y), (shadow_size*2, y))
    
    pygame.image.save(scroll, IMGFILEPATH["scroll"])
    images["scroll"] = scroll
    
    return images

# Helper function to draw a heart shape
def draw_heart(surface, x, y, size, color):
    # Heart shape is made of two circles and a triangle
    radius = size // 2
    
    # Two circles for the top lobes
    pygame.draw.circle(surface, color, (x - radius//2, y - radius//2), radius)
    pygame.draw.circle(surface, color, (x + radius//2, y - radius//2), radius)
    
    # Triangle for the bottom point
    points = [
        (x - size//2, y - radius//3),
        (x + size//2, y - radius//3),
        (x, y + size//2)
    ]
    pygame.draw.polygon(surface, color, points)

# Initialize Pygame with enhanced setup
def setup(GUI=True):
    global screen, images, WIDTH, HEIGHT, CELL_SIZE, GAME_AREA_HEIGHT, CONSOLE_HEIGHT, clock
    
    if GUI:
        pygame.init()
        
        # Get display info to adjust for screen size
        info = pygame.display.Info()
        available_width = min(info.current_w - 50, 1024)  # Slightly larger max width
        available_height = min(info.current_h - 100, 900)
        
        # Recalculate dimensions based on available space
        CELL_SIZE = min(available_width // GRID_SIZE, 140)  # Slightly larger cells
        WIDTH = CELL_SIZE * GRID_SIZE
        GAME_AREA_HEIGHT = CELL_SIZE * GRID_SIZE
        CONSOLE_HEIGHT = min(280, available_height - GAME_AREA_HEIGHT)  # Slightly larger console
        HEIGHT = GAME_AREA_HEIGHT + CONSOLE_HEIGHT
        
        # Set up display with a more descriptive title
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Castle Escape - Medieval Dungeon Adventure")
        
        # Set up clock for controlling game speed
        clock = pygame.time.Clock()
        
        # Load all images
        images = load_images()
        
        # Set custom icon if available
        try:
            icon = images["player"]
            pygame.display.set_icon(icon)
        except:
            pass

# Map room to grid cell positions
def position_to_grid(position):
    row, col = position
    return col * CELL_SIZE, row * CELL_SIZE

    # Draw the castle rooms with improved atmosphere
def draw_rooms():
    # Draw stone background
    screen.blit(images["background"], (0, 0))
    
    # Draw floor tiles
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
            screen.blit(images["stone_floor"], (x, y))
    
    # Draw horizontal walls
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
            screen.blit(images["wall_h"], (x, y))
            if y + CELL_SIZE < GAME_AREA_HEIGHT:
                screen.blit(images["wall_h"], (x, y + CELL_SIZE - images["wall_h"].get_height()))
    
    # Draw vertical walls
    for y in range(0, GAME_AREA_HEIGHT, CELL_SIZE):
        for x in range(0, WIDTH, CELL_SIZE):
            screen.blit(images["wall_v"], (x, y))
            if x + CELL_SIZE < WIDTH:
                screen.blit(images["wall_v"], (x + CELL_SIZE - images["wall_v"].get_width(), y))
    
    # Draw Console area with more texture and depth
    console_rect = pygame.Rect(0, GAME_AREA_HEIGHT, WIDTH, CONSOLE_HEIGHT)
    pygame.draw.rect(screen, CONSOLE_BG, console_rect)
    
    # Draw decorative border for console
    border_width = 4
    pygame.draw.rect(screen, (60, 40, 20), console_rect, border_width)
    
    # Add stone accents at console corners
    corner_size = 15
    for x, y in [(0, GAME_AREA_HEIGHT), 
                 (WIDTH - corner_size, GAME_AREA_HEIGHT),
                 (0, HEIGHT - corner_size),
                 (WIDTH - corner_size, HEIGHT - corner_size)]:
        pygame.draw.rect(screen, (80, 60, 40), (x, y, corner_size, corner_size))
        pygame.draw.rect(screen, (100, 80, 60), (x+2, y+2, corner_size-4, corner_size-4))

# Draw the goal room with treasure effects
def draw_goal_room():
    x, y = position_to_grid(game.goal_room)
    screen.blit(images["goal_room"], (x, y))
    
    # Add animated sparkle effects
    global animation_frame
    sparkle_count = 5
    
    for i in range(sparkle_count):
        # Calculate position with slight movement
        sparkle_x = x + CELL_SIZE//2 + int(10 * math.cos((animation_frame + i*20) * 0.1))
        sparkle_y = y + CELL_SIZE//2 + int(10 * math.sin((animation_frame + i*20) * 0.1))
        
        # Calculate size that pulses
        sparkle_size = 2 + int(2 * math.sin(animation_frame * 0.2 + i))
        
        # Draw sparkle
        pygame.draw.circle(screen, (255, 255, 200), (sparkle_x, sparkle_y), sparkle_size)

# Draw player at a given position with animation effects
def draw_player(position):
    x, y = position_to_grid(position)
    player_img = images["player"]
    
    # Add slight hovering animation for player
    global animation_frame
    hover_offset = int(2 * math.sin(animation_frame * 0.1))
    
    player_x = x + (CELL_SIZE - player_img.get_width()) // 2
    player_y = y + (CELL_SIZE - player_img.get_height()) // 2 + hover_offset
    
    # Draw a subtle shadow beneath the player
    shadow_radius = player_img.get_width() // 3
    shadow_y_offset = 5
    pygame.draw.ellipse(screen, (0, 0, 0, 128), 
                      (player_x + (player_img.get_width() - shadow_radius)//2, 
                       player_y + player_img.get_height() - shadow_y_offset, 
                       shadow_radius, shadow_radius//2))
    
    screen.blit(player_img, (player_x, player_y))

# Draw guards at their positions with animation
def draw_guards(guard_positions):
    global animation_frame
    
    for guard, position in guard_positions.items():
        x, y = position_to_grid(position)
        guard_img = images["guard"]
        
        # Add patrol animation - slight movement back and forth
        patrol_offset = int(3 * math.sin(animation_frame * 0.05))
        
        guard_x = x + (CELL_SIZE - guard_img.get_width()) // 2 + patrol_offset
        guard_y = y + (CELL_SIZE - guard_img.get_height()) // 2
        
        # Draw guard shadow
        shadow_radius = guard_img.get_width() // 3
        shadow_y_offset = 5
        pygame.draw.ellipse(screen, (0, 0, 0, 128), 
                          (guard_x + (guard_img.get_width() - shadow_radius)//2, 
                           guard_y + guard_img.get_height() - shadow_y_offset, 
                           shadow_radius, shadow_radius//2))
        
        screen.blit(guard_img, (guard_x, guard_y))
        
        # Label the guard with improved styling
        font_size = max(14, min(24, CELL_SIZE // 5))
        try:
            font = pygame.font.SysFont("medievalsharp", font_size)
        except:
            font = pygame.font.Font(None, font_size)
        
        # Add a background for the label
        label = font.render(guard, True, WHITE)
        label_bg = pygame.Rect(
            x + CELL_SIZE - label.get_width() - 10, 
            y + 5,
            label.get_width() + 6,
            label.get_height() + 2
        )
        pygame.draw.rect(screen, (80, 0, 0), label_bg)
        pygame.draw.rect(screen, (120, 0, 0), label_bg, 1)
        
        screen.blit(label, (x + CELL_SIZE - label.get_width() - 7, y + 6))

# Draw player and guard together with improved conflict visualization
def draw_player_and_guard_together(position, guard_positions):
    guards_in_room = [guard for guard, pos in guard_positions.items() if pos == position]
    guards_not_in_room = [guard for guard in guard_positions if guard not in guards_in_room]
    
    if guards_in_room:
        x, y = position_to_grid(position)
        player_img = images["player"]
        guard_img = images["guard"]
        
        # Position player on the left third of the cell
        player_x = x + CELL_SIZE // 6
        player_y = y + (CELL_SIZE - player_img.get_height()) // 2
        
        # Position guard on the right third of the cell
        guard_x = x + 2 * CELL_SIZE // 3
        guard_y = y + (CELL_SIZE - guard_img.get_height()) // 2
        
        # Draw battle effect background
        global animation_frame
        battle_intensity = abs(math.sin(animation_frame * 0.2))
        
        # Draw pulsing battle aura
        aura_radius = int(CELL_SIZE * 0.4 * (0.8 + 0.2 * battle_intensity))
        aura_alpha = int(100 + 50 * battle_intensity)
        
        # Create a surface for the battle aura with transparency
        aura_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (255, 0, 0, aura_alpha), 
                         (CELL_SIZE//2, CELL_SIZE//2), aura_radius)
        
        # Draw the aura
        screen.blit(aura_surface, (x, y))
        
        # Draw sword clash effect between them
        clash_x = (player_x + player_img.get_width() + guard_x) // 2
        clash_y = (player_y + guard_y + guard_img.get_height()//2) // 2
        
        # Draw "spark" effects for the clash
        for _ in range(5):
            spark_angle = random.random() * 6.28
            spark_dist = random.randint(5, 15)
            spark_x = clash_x + int(spark_dist * math.cos(spark_angle))
            spark_y = clash_y + int(spark_dist * math.sin(spark_angle))
            spark_size = random.randint(1, 3)
            pygame.draw.circle(screen, (255, 255, 200), (spark_x, spark_y), spark_size)
        
        # Draw clash "star"
        clash_size = 10 + int(5 * battle_intensity)
        clash_points = []
        for i in range(8):
            angle = i * 6.28 / 8
            dist = clash_size if i % 2 == 0 else clash_size // 2
            clash_points.append((
                clash_x + int(dist * math.cos(angle)),
                clash_y + int(dist * math.sin(angle))
            ))
        pygame.draw.polygon(screen, (255, 255, 100), clash_points)
        
        # Draw shadows
        shadow_radius = player_img.get_width() // 3
        shadow_y_offset = 5
        
        pygame.draw.ellipse(screen, (0, 0, 0, 128), 
                          (player_x + (player_img.get_width() - shadow_radius)//2, 
                           player_y + player_img.get_height() - shadow_y_offset, 
                           shadow_radius, shadow_radius//2))
        
        pygame.draw.ellipse(screen, (0, 0, 0, 128), 
                          (guard_x + (guard_img.get_width() - shadow_radius)//2, 
                           guard_y + guard_img.get_height() - shadow_y_offset, 
                           shadow_radius, shadow_radius//2))
        
        # Draw the characters
        screen.blit(player_img, (player_x, player_y))
        screen.blit(guard_img, (guard_x, guard_y))
        
        # Draw exclamation with animation
        font_size = max(24, min(40, CELL_SIZE // 3))
        try:
            font = pygame.font.SysFont("medievalsharp", font_size, bold=True)
        except:
            font = pygame.font.Font(None, font_size)
        
        # Animated warning symbol
        warning_y_offset = int(5 * math.sin(animation_frame * 0.2))
        conflict = font.render("!", True, (255, 50, 50))
        
        # Add a glow effect to the warning
        glow_surface = pygame.Surface((conflict.get_width()+10, conflict.get_height()+10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 0, 0, 100), 
                         (glow_surface.get_width()//2, glow_surface.get_height()//2), 
                         glow_surface.get_width()//2)
        
        screen.blit(glow_surface, 
                  (x + CELL_SIZE//2 - glow_surface.get_width()//2, 
                   y + 5 + warning_y_offset - 5))
        
        screen.blit(conflict, 
                  (x + CELL_SIZE//2 - conflict.get_width()//2, 
                   y + 5 + warning_y_offset))
        
        # Label the guard
        guard_label_font_size = max(14, min(24, CELL_SIZE // 5))
        try:
            guard_label_font = pygame.font.SysFont("medievalsharp", guard_label_font_size)
        except:
            guard_label_font = pygame.font.Font(None, guard_label_font_size)
        
        # Add a background for the label
        label = guard_label_font.render(guards_in_room[0], True, WHITE)
        label_bg = pygame.Rect(
            x + CELL_SIZE - label.get_width() - 10, 
            y + 5,
            label.get_width() + 6,
            label.get_height() + 2
        )
        pygame.draw.rect(screen, (80, 0, 0), label_bg)
        pygame.draw.rect(screen, (120, 0, 0), label_bg, 1)
        
        screen.blit(label, (x + CELL_SIZE - label.get_width() - 7, y + 6))

    # Draw the guards that are not in the same room as player
    for guard in guards_not_in_room:
        draw_guards({guard: guard_positions[guard]})

# Draw player health status with improved visuals
def draw_health(health):
    health_str = game.int_to_health_state[health] if isinstance(health, int) else health
    
    # Calculate position for health bar
    health_x = 15
    health_y = GAME_AREA_HEIGHT + 15
    
    # Draw health bar frame
    screen.blit(images["health_bar"], (health_x, health_y))
    
    health_width = images["health_full"].get_width()
    health_height = images["health_full"].get_height()
    
    # Draw appropriate health indicator
    if health_str == 'Full':
        screen.blit(images["health_full"], (health_x + 5, health_y + 5))
        
        # Add pulsing glow effect for full health
        glow_radius = 3 + int(math.sin(animation_frame * 0.1) * 2)
        glow_surface = pygame.Surface((health_width+10, health_height+10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (0, 255, 0, 30), 
                       (0, 0, health_width+10, health_height+10), 
                       glow_radius)
        screen.blit(glow_surface, (health_x, health_y))
        
    elif health_str == 'Injured':
        screen.blit(images["health_injured"], (health_x + 5, health_y + 5))
        
        # Add warning glow effect for injured health
        if animation_frame % 30 < 15:  # Blink warning
            glow_surface = pygame.Surface((health_width+10, health_height+10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 150, 0, 30), 
                           (0, 0, health_width+10, health_height+10), 
                           2)
            screen.blit(glow_surface, (health_x, health_y))
            
    else:  # Critical
        screen.blit(images["health_critical"], (health_x + 5, health_y + 5))
        
        # Add alarm glow effect for critical health
        glow_intensity = abs(math.sin(animation_frame * 0.2)) * 50 + 30
        glow_surface = pygame.Surface((health_width+10, health_height+10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 0, 0, int(glow_intensity)), 
                       (0, 0, health_width+10, health_height+10), 
                       3)
        screen.blit(glow_surface, (health_x, health_y))
    
    # Draw health text with improved styling
    health_text_x = health_x + images["health_bar"].get_width() + 15
    health_text_y = health_y + 10
    
    font_size = max(16, min(28, CONSOLE_HEIGHT // 8))
    try:
        font = pygame.font.SysFont("medievalsharp", font_size)
    except:
        font = pygame.font.Font(None, font_size)
    
    # Add text shadow for depth
    health_text = f"Health: {health_str}"
    shadow = font.render(health_text, True, (40, 40, 40))
    text = font.render(health_text, True, 
                    (220, 220, 180) if health_str == 'Full' else
                    (220, 180, 100) if health_str == 'Injured' else
                    (220, 100, 100))
    
    screen.blit(shadow, (health_text_x + 2, health_text_y + 2))
    screen.blit(text, (health_text_x, health_text_y))

# Display Controls with medieval styling
def display_controls():
    # Calculate position for controls panel
    controls_width = images["controls_panel"].get_width()
    controls_height = images["controls_panel"].get_height()
    controls_x = WIDTH - controls_width - 15
    controls_y = GAME_AREA_HEIGHT + 15
    
    # Draw control panel background
    screen.blit(images["controls_panel"], (controls_x, controls_y))
    
    # Scale font based on available space
    font_size = max(14, min(24, controls_height // 10))
    try:
        font = pygame.font.SysFont("medievalsharp", font_size)
        title_font = pygame.font.SysFont("medievalsharp", font_size + 4, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
        title_font = pygame.font.Font(None, font_size + 4)
    
    controls = [
        ("Move:", (180, 160, 120)),
        ("W - Up", TEXT_COLOR),
        ("S - Down", TEXT_COLOR),
        ("A - Left", TEXT_COLOR),
        ("D - Right", TEXT_COLOR),
        ("Actions:", (180, 160, 120)),
        ("F - Fight", TEXT_COLOR),
        ("H - Hide", TEXT_COLOR)
    ]
    
    # Draw title
    title = title_font.render("Commands", True, (200, 180, 140))
    title_x = controls_x + (controls_width - title.get_width()) // 2
    screen.blit(title, (title_x, controls_y + 15))
    
    # Draw decorative separator
    separator_y = controls_y + 15 + title.get_height() + 5
    pygame.draw.line(screen, (120, 100, 80), 
                   (controls_x + 20, separator_y), 
                   (controls_x + controls_width - 20, separator_y), 
                   2)
    
    # Draw control instructions with improved styling
    y_pos = separator_y + 10
    indent = 20
    
    for i, (line, color) in enumerate(controls):
        # Check if this is a section header
        is_header = line.endswith(":")
        
        # Use appropriate font and indentation
        text_font = title_font if is_header else font
        text_x = controls_x + (indent if not is_header else 15)
        
        # Create text with shadow for depth
        shadow = text_font.render(line, True, (60, 50, 40))
        text = text_font.render(line, True, color)
        
        # Draw text with shadow
        screen.blit(shadow, (text_x + 1, y_pos + 1))
        screen.blit(text, (text_x, y_pos))
        
        # Update position for next line
        y_pos += text.get_height() + (10 if is_header else 5)
    
    # Draw decorative corner accents
    accent_size = 8
    accent_points = [
        (controls_x + 5, controls_y + 5),
        (controls_x + controls_width - 5 - accent_size, controls_y + 5),
        (controls_x + 5, controls_y + controls_height - 5 - accent_size),
        (controls_x + controls_width - 5 - accent_size, controls_y + controls_height - 5 - accent_size)
    ]
    
    for x, y in accent_points:
        pygame.draw.rect(screen, (150, 130, 100), (x, y, accent_size, accent_size))
        pygame.draw.rect(screen, (120, 100, 80), (x, y, accent_size, accent_size), 1)

# Display victory or defeat message with enhanced effects
def display_end_message(message):
    global animation_frame
    
    # Add screen darkening effect
    overlay = pygame.Surface((WIDTH, GAME_AREA_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Transparent black
    screen.blit(overlay, (0, 0))
    
    if message == "Victory!":
        victory_image = images["victory"]
        x = WIDTH // 2 - victory_image.get_width() // 2
        y = GAME_AREA_HEIGHT // 2 - victory_image.get_height() // 2
        
        # Add victory glow effect
        glow_size = 20 + int(10 * math.sin(animation_frame * 0.1))
        glow_surface = pygame.Surface((victory_image.get_width() + glow_size*2, 
                                     victory_image.get_height() + glow_size*2), 
                                    pygame.SRCALPHA)
        
        # Draw multiple glowing rings
        for i in range(glow_size, 0, -5):
            alpha = max(0, min(150, int(200 * (i / glow_size))))
            pygame.draw.rect(glow_surface, (255, 215, 0, alpha), 
                           (glow_size - i, glow_size - i, 
                            victory_image.get_width() + i*2, 
                            victory_image.get_height() + i*2), 
                           5)
        
        # Draw the glow
        screen.blit(glow_surface, 
                  (x - glow_size, y - glow_size))
        
        # Draw victory image
        screen.blit(victory_image, (x, y))
        
        # Draw celebratory particles
        for _ in range(10):
            particle_x = random.randint(0, WIDTH)
            particle_y = random.randint(0, GAME_AREA_HEIGHT)
            particle_size = random.randint(2, 5)
            particle_color = random.choice([
                (255, 215, 0),  # Gold
                (255, 255, 255),  # White
                (220, 220, 150)   # Light gold
            ])
            pygame.draw.circle(screen, particle_color, (particle_x, particle_y), particle_size)
        
    else:  # Defeat
        defeat_image = images["defeat"]
        x = WIDTH // 2 - defeat_image.get_width() // 2
        y = GAME_AREA_HEIGHT // 2 - defeat_image.get_height() // 2
        
        # Add defeat effect - red pulsing glow
        glow_size = 15 + int(5 * math.sin(animation_frame * 0.1))
        glow_surface = pygame.Surface((defeat_image.get_width() + glow_size*2, 
                                     defeat_image.get_height() + glow_size*2), 
                                    pygame.SRCALPHA)
        
        # Draw multiple glowing rings
        for i in range(glow_size, 0, -3):
            alpha = max(0, min(150, int(200 * (i / glow_size))))
            pygame.draw.rect(glow_surface, (150, 0, 0, alpha), 
                           (glow_size - i, glow_size - i, 
                            defeat_image.get_width() + i*2, 
                            defeat_image.get_height() + i*2), 
                           3)
        
        # Draw the glow
        screen.blit(glow_surface, 
                  (x - glow_size, y - glow_size))
        
        # Draw defeat image
        screen.blit(defeat_image, (x, y))
        
        # Draw smoke-like particles
        for _ in range(15):
            particle_x = random.randint(0, WIDTH)
            particle_y = random.randint(0, GAME_AREA_HEIGHT)
            particle_size = random.randint(3, 8)
            particle_color = random.choice([
                (100, 0, 0, 150),  # Dark red
                (50, 50, 50, 150),  # Dark gray
                (70, 0, 0, 150)     # Another red shade
            ])
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, 
                             (particle_size, particle_size), particle_size)
            screen.blit(particle_surface, (particle_x, particle_y))

# Enhanced console display styled as a medieval scroll
def draw_console(action_results):
    # Draw scroll background
    scroll_x = 10
    scroll_y = GAME_AREA_HEIGHT + images["health_bar"].get_height() + 30
    
    # Adjust scroll dimensions to fit available space
    scroll_height = CONSOLE_HEIGHT - images["health_bar"].get_height() - 40
    scroll_width = WIDTH - 20
    
    # Scale the scroll image to fit
    scroll_img = pygame.transform.scale(images["scroll"], (scroll_width, scroll_height))
    screen.blit(scroll_img, (scroll_x, scroll_y))
    
    # Draw console header
    font_size = max(16, min(30, CONSOLE_HEIGHT // 10))
    try:
        font = pygame.font.SysFont("medievalsharp", font_size, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
    
    console_title = font.render("Adventure Chronicle", True, (80, 40, 0))
    title_x = scroll_x + (scroll_width - console_title.get_width()) // 2
    screen.blit(console_title, (title_x, scroll_y + 10))
    
    # Draw separator with decorative ends
    line_y = scroll_y + console_title.get_height() + 15
    line_width = scroll_width - 40
    line_x = scroll_x + (scroll_width - line_width) // 2
    
    # Draw main line
    pygame.draw.line(screen, (120, 80, 40), 
                   (line_x, line_y),
                   (line_x + line_width, line_y), 2)
    
    # Draw decorative end caps
    cap_size = 6
    for x in [line_x, line_x + line_width]:
        pygame.draw.circle(screen, (120, 80, 40), (x, line_y), cap_size)
        pygame.draw.circle(screen, (150, 100, 50), (x, line_y), cap_size - 2)
    
    # Display action results with medieval styling
    font_size = max(12, min(20, CONSOLE_HEIGHT // 15))
    try:
        font = pygame.font.SysFont("medievalsharp", font_size)
        action_font = pygame.font.SysFont("medievalsharp", font_size, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
        action_font = pygame.font.Font(None, font_size)
    
    line_height = font_size + 4
    log_start_y = line_y + 15
    available_lines = (scroll_height - (log_start_y - scroll_y) - 10) // line_height
    
    # Filter out None values and keep only the most recent entries
    valid_results = [r for r in action_results if r]
    display_results = valid_results[-available_lines:] if valid_results else []
    
    for i, result in enumerate(display_results):
        if len(result) > 0:
            # Format the text in a medieval style
            if "Action:" in result and "Result:" in result:
                # Extract action type
                action_start = result.find("Action: ") + 8
                action_end = result.find(",", action_start)
                if action_end == -1:
                    action_end = result.find("Result:", action_start)
                action_text = result[action_start:action_end].strip()
                
                # Get health and position info
                result_text = result[result.find("Result:"):]
                health_text = "Unknown"
                pos_text = "Unknown"
                
                if "{" in result_text:
                    pos_start = result_text.find("'player_position': ") + 19
                    pos_end = result_text.find("}", pos_start)
                    if pos_end > pos_start:
                        pos_text = result_text[pos_start:pos_end].strip()
                    
                    health_start = result_text.find("'player_health': ") + 17
                    health_end = result_text.find(",", health_start)
                    if health_end > health_start:
                        health_text = result_text[health_start:health_end].strip()
                        if health_text.isdigit():
                            health_text = game.int_to_health_state[int(health_text)]
                
                # Create stylized log entry
                y_pos = log_start_y + i * line_height
                
                # Draw log entry with bullet point
                bullet_x = scroll_x + 20
                text_x = bullet_x + 15
                
                # Draw decorative bullet
                pygame.draw.circle(screen, (80, 40, 0), (bullet_x, y_pos + line_height//2 - 1), 3)
                
                # Draw the action (like "MOVE" or "FIGHT")
                action_surface = action_font.render(action_text, True, (120, 60, 0))
                screen.blit(action_surface, (text_x, y_pos))
                
                # Draw position and health info
                info_x = text_x + action_surface.get_width() + 10
                info_text = f"→ Position: {pos_text}"
                if health_text != "Unknown":
                    # Color code health text
                    health_color = (0, 100, 0) if health_text == "Full" else \
                                  (180, 100, 0) if health_text == "Injured" else \
                                  (150, 0, 0)
                    
                    info_surface = font.render(info_text, True, (60, 30, 0))
                    screen.blit(info_surface, (info_x, y_pos))
                    
                    health_x = info_x + info_surface.get_width() + 10
                    health_surface = font.render(f"Health: {health_text}", True, health_color)
                    screen.blit(health_surface, (health_x, y_pos))
                else:
                    # Just show position if health unknown
                    info_surface = font.render(info_text, True, (60, 30, 0))
                    screen.blit(info_surface, (info_x, y_pos))
            else:
                # For other messages just show the text
                y_pos = log_start_y + i * line_height
                text_surface = font.render(result[:min(len(result), 80)], True, (60, 30, 0))
                screen.blit(text_surface, (scroll_x + 20, y_pos))

# Import added for math functions
import math

# Main loop with animation and improved timing
def main():
    global game_ended, action_results, animation_frame
    clock = pygame.time.Clock()
    running = True
    end_message = ""
    animation_frame = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not game_ended:
                    action = "UP"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                if event.key == pygame.K_s and not game_ended:
                    action = "DOWN"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                if event.key == pygame.K_a and not game_ended:
                    action = "LEFT"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                if event.key == pygame.K_d and not game_ended:
                    action = "RIGHT"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                if event.key == pygame.K_f and not game_ended:
                    action = "FIGHT"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                if event.key == pygame.K_h and not game_ended:
                    action = "HIDE"
                    result = game.step(action)
                    action_results.append(f"Action: {action}, Result: {result}")
                    
                # Keep only the latest results that fit
                if len(action_results) > 10:
                    action_results = action_results[-10:]
        
        # Clear screen
        screen.fill(BLACK)
        
        # Update animation frame
        animation_frame += 1
        
        # Draw the castle rooms
        draw_rooms()
        
        # Draw the goal room with effects
        draw_goal_room()

        # Check if player and a guard are in the same room
        if game.current_state['player_position'] in game.current_state['guard_positions'].values():
            draw_player_and_guard_together(game.current_state['player_position'], 
                                         game.current_state['guard_positions'])
        else:
            # Draw the player and guards in separate positions
            draw_player(game.current_state['player_position'])
            draw_guards(game.current_state['guard_positions'])

        # Display player health with effects
        draw_health(game.current_state['player_health'])
        
        # Display controls with medieval styling
        # display_controls()

        # Check for terminal state
        if game.is_terminal() == 'goal':
            game_ended = True
            end_message = "Victory!"
        elif game.is_terminal() == 'defeat':
            game_ended = True
            end_message = "Defeat!"

        if game_ended:
            display_end_message(end_message)
            
            # Reset game after a moment (allow player to see the end message)
            if animation_frame % 180 == 0:  # Reset after about a 6 seconds
                game.reset()
                game_ended = False
                end_message = ""
                action_results = [None, None, None, None, None]

        # Draw the console with styled action results
        draw_console(action_results)

        pygame.display.flip()
    
        clock.tick(30)  # Limit to 30 FPS for smooth animation

    pygame.quit()
    sys.exit()

# Modified refresh function for agent integration
def refresh(obs, reward, done, info, delay=0.1):
    global fps, sleeptime, game_ended, clock, action_results, game, animation_frame
    
    animation_frame += 1
    
    try:
        action = info['action']
    except:
        action = "None"

    result = "Pos: {}, Health: {}, Guard In Cell: {}, Reward: {}, Action: {}".format(
        obs['player_position'], 
        game.int_to_health_state[obs['player_health']], 
        obs['guard_in_cell'], 
        reward, 
        action
    )

    if None in action_results:
        action_results[action_results.index(None)] = result
    else:
        action_results.pop(0)
        action_results.append(result)

    fps = 60
    clock = pygame.time.Clock()
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw the castle rooms with atmosphere
    draw_rooms()
    
    # Draw the goal room with effects
    draw_goal_room()

    # Check if player and a guard are in the same room
    if game.current_state['player_position'] in game.current_state['guard_positions'].values():
        draw_player_and_guard_together(game.current_state['player_position'], 
                                     game.current_state['guard_positions'])
    else:
        # Draw the player and guards in separate positions
        draw_player(game.current_state['player_position'])
        draw_guards(game.current_state['guard_positions'])

    # Display player health with effects
    draw_health(game.current_state['player_health'])
    
    # Display controls with medieval styling
    display_controls()

    # Check for terminal state
    if game.is_terminal() == 'goal':
        game_ended = True
        end_message = "Victory!"
        display_end_message(end_message)
    elif game.is_terminal() == 'defeat':
        game_ended = True
        end_message = "Defeat!"
        display_end_message(end_message)

    # Draw the console with styled action results
    draw_console(action_results)

    pygame.display.flip()
    clock.tick(fps)
    time.sleep(sleeptime)

if __name__ == "__main__":
    setup()
    main()