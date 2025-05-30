import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 1000
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Badminton Championship")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COURT_GREEN = (60, 179, 113)  # Medium sea green (more vibrant)
COURT_LINES = (255, 255, 255)
NET_COLOR = (220, 220, 220)
PLAYER_COLOR = (255, 50, 50)  # Brighter red
COMPUTER_COLOR = (50, 50, 255)  # Brighter blue
SHUTTLE_COLOR = (255, 255, 240)
TEXT_COLOR = (255, 255, 0)
MENU_BG_COLOR = (25, 25, 112)  # Midnight Blue
BUTTON_COLOR = (46, 196, 182)
BUTTON_HOVER_COLOR = (80, 220, 200)

# Game constants
FPS = 60
GRAVITY = 0.4
AIR_RESISTANCE = 0.98
PLAYER_SPEED = 7  # Increased from 5
COMPUTER_SPEED = 5  # Increased from 4
PLAYER_WIDTH = 40  # Increased from 30
PLAYER_HEIGHT = 70  # Increased from 60
SHUTTLE_RADIUS = 10  # Increased from 8
NET_WIDTH = 5
NET_HEIGHT = 180  # Increased from 150
COURT_WIDTH = WIDTH - 100  # 50px margin on each side
COURT_HEIGHT = HEIGHT - 100  # 50px margin on top and bottom
COURT_TOP = 50
COURT_BOTTOM = COURT_TOP + COURT_HEIGHT
COURT_LEFT = 50
COURT_RIGHT = COURT_LEFT + COURT_WIDTH
NET_X = WIDTH // 2
NET_TOP = COURT_BOTTOM - NET_HEIGHT
FLOOR_Y = COURT_BOTTOM

# Game states
MENU = 0
PLAYING = 1
SERVE = 2
POINT_SCORED = 3
GAME_OVER = 4

# Initialize game variables
game_state = MENU
player_score = 0
computer_score = 0
winning_score = 11  # First to 11 points
serving = True  # Player serves first
rally_started = False

# Player class
class Player:
    def __init__(self, x, y, is_computer=False):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = COMPUTER_SPEED if is_computer else PLAYER_SPEED
        self.color = COMPUTER_COLOR if is_computer else PLAYER_COLOR
        self.is_computer = is_computer
        self.swinging = False
        self.swing_cooldown = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.jump_speed = 0
        self.jumping = False
        self.on_ground = True
        self.jump_height = -12
        self.jump_cooldown = 0
        
    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
        elif direction == "jump" and self.on_ground and self.jump_cooldown <= 0:
            self.jump_speed = self.jump_height
            self.jumping = True
            self.on_ground = False
            self.jump_cooldown = 30  # Prevent continuous jumping
        
        # Boundary checks
        if self.is_computer:
            # Computer stays on right side
            self.x = max(NET_X + 10, min(self.x, COURT_RIGHT - self.width))
        else:
            # Player stays on left side
            self.x = max(COURT_LEFT, min(self.x, NET_X - self.width - 10))
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def swing(self):
        if self.swing_cooldown <= 0:
            self.swinging = True
            self.swing_cooldown = 20  # Cooldown frames
            return True
        return False
    
    def update(self):
        # Handle jumping physics
        if not self.on_ground:
            self.y += self.jump_speed
            self.jump_speed += 0.8  # Gravity effect
            
            # Check if landed
            if self.y >= FLOOR_Y - self.height:
                self.y = FLOOR_Y - self.height
                self.on_ground = True
                self.jumping = False
                self.jump_speed = 0
        
        # Update cooldowns
        if self.swing_cooldown > 0:
            self.swing_cooldown -= 1
        else:
            self.swinging = False
            
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self):
        # Draw player body
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw player head
        head_radius = 15
        head_y = self.y - head_radius // 2
        head_x = self.x + self.width // 2
        pygame.draw.circle(screen, self.color, (head_x, head_y), head_radius)
        
        # Draw racket when swinging
        if self.swinging:
            racket_color = (255, 165, 0)  # Orange
            if self.is_computer:
                # Draw racket on left side for computer
                racket_x = self.x - 25
                racket_y = self.y + 20
                # Draw racket handle
                pygame.draw.line(screen, (139, 69, 19), (self.x + 5, self.y + 25), 
                                (racket_x + 15, racket_y + 10), 5)
                # Draw racket head
                pygame.draw.ellipse(screen, racket_color, (racket_x, racket_y, 30, 25), 3)
            else:
                # Draw racket on right side for player
                racket_x = self.x + self.width
                racket_y = self.y + 20
                # Draw racket handle
                pygame.draw.line(screen, (139, 69, 19), (self.x + self.width - 5, self.y + 25), 
                                (racket_x + 15, racket_y + 10), 5)
                # Draw racket head
                pygame.draw.ellipse(screen, racket_color, (racket_x, racket_y, 30, 25), 3)

# Shuttlecock class
class Shuttlecock:
    def __init__(self):
        self.reset()
        # Load shuttlecock images for animation
        self.shuttle_frames = []
        self.frame_index = 0
        self.animation_speed = 0.2
        self.shuttle_trail = []  # Store positions for trail effect
        self.max_trail_length = 10
    
    def reset(self, for_serve=True, server_is_player=True):
        if for_serve:
            if server_is_player:
                self.x = COURT_LEFT + 100
                self.vx = 2  # Initial velocity for serve
            else:
                self.x = COURT_RIGHT - 100
                self.vx = -2  # Initial velocity for serve
            self.y = HEIGHT // 2
            self.vy = -10  # Initial upward velocity
        else:
            # Reset to middle for non-serve situations
            self.x = WIDTH // 2
            self.y = HEIGHT // 3
            self.vx = random.choice([-3, 3])
            self.vy = -8
        
        self.radius = SHUTTLE_RADIUS
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
        self.shuttle_trail = []  # Clear trail on reset
        self.frame_index = 0
    
    def update(self):
        # Store current position for trail effect
        self.shuttle_trail.append((self.x, self.y))
        if len(self.shuttle_trail) > self.max_trail_length:
            self.shuttle_trail.pop(0)
        
        # Update animation frame
        self.frame_index += self.animation_speed
        if self.frame_index >= 4:  # Assuming 4 frames of animation
            self.frame_index = 0
            
        # Apply physics
        self.vy += GRAVITY
        self.vx *= AIR_RESISTANCE
        self.vy *= AIR_RESISTANCE
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Update rectangle position
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        
        # Check for net collision
        net_rect = pygame.Rect(NET_X - NET_WIDTH // 2, NET_TOP, NET_WIDTH, NET_HEIGHT)
        if self.rect.colliderect(net_rect):
            # Bounce off net with reduced velocity
            if self.x < NET_X:
                self.x = NET_X - NET_WIDTH // 2 - self.radius
            else:
                self.x = NET_X + NET_WIDTH // 2 + self.radius
            self.vx = -self.vx * 0.5
            self.vy *= 0.8
            # Play net hit sound
            # net_hit_sound.play()
        
        # Check for wall collisions
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * 0.8
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * 0.8
        
        # Check if hit floor
        return self.y + self.radius >= FLOOR_Y
    
    def hit(self, player, power=10):
        # Calculate hit direction and power
        if player.is_computer:
            # Computer aims toward player's side with more strategy
            # Sometimes aim for corners, sometimes for middle
            target_type = random.randint(0, 10)
            if target_type < 3:  # 30% chance for corner shot
                target_x = random.choice([COURT_LEFT + 30, NET_X - 80])
            elif target_type < 7:  # 40% chance for middle shot
                target_x = (COURT_LEFT + NET_X) // 2
            else:  # 30% chance for random shot
                target_x = random.randint(COURT_LEFT, NET_X - 50)
                
            dx = target_x - self.x
            self.vx = dx * 0.05
            
            # Vary power based on position
            if player.y < FLOOR_Y - player.height - 20:  # If computer is jumping
                self.vy = -power * 1.2  # More powerful hit
            else:
                self.vy = -power
        else:
            # Player hits toward computer's side
            # More control based on player position relative to shuttlecock
            dx = self.x - player.x
            if dx < player.width // 2:  # Hit on left side
                target_x = NET_X + 50 + random.randint(0, 100)
            else:  # Hit on right side
                target_x = COURT_RIGHT - 50 - random.randint(0, 100)
                
            dx = target_x - self.x
            self.vx = dx * 0.05
            
            # Vary power based on player's position
            if not player.on_ground:  # If player is jumping
                self.vy = -power * 1.3  # Smash!
            else:
                self.vy = -power
        
        # Add slight randomness to make game less predictable
        self.vx += random.uniform(-0.5, 0.5)
        self.vy += random.uniform(-0.5, 0.5)
        
        # Play hit sound
        # hit_sound.play()
    
    def draw(self):
        # Draw trail effect
        for i, (trail_x, trail_y) in enumerate(self.shuttle_trail):
            # Make trail fade out
            alpha = int(255 * (i / len(self.shuttle_trail)))
            radius = int(self.radius * (0.3 + 0.7 * i / len(self.shuttle_trail)))
            trail_color = (255, 255, 240, alpha)
            
            # Create a surface for the trail circle with alpha
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (radius, radius), radius)
            screen.blit(trail_surface, (trail_x - radius, trail_y - radius))
        
        # Draw shuttlecock
        pygame.draw.circle(screen, SHUTTLE_COLOR, (int(self.x), int(self.y)), self.radius)
        
        # Draw feathers
        feather_length = self.radius * 1.5
        angle = math.atan2(self.vy, self.vx) + math.pi  # Point feathers opposite to movement
        
        # Draw multiple feathers
        for i in range(4):
            feather_angle = angle + i * math.pi / 2
            end_x = self.x + math.cos(feather_angle) * feather_length
            end_y = self.y + math.sin(feather_angle) * feather_length
            pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 2)

# Initialize objects
player = Player(COURT_LEFT + 50, FLOOR_Y - PLAYER_HEIGHT)
computer = Player(COURT_RIGHT - 50 - PLAYER_WIDTH, FLOOR_Y - PLAYER_HEIGHT, is_computer=True)
shuttlecock = Shuttlecock()

# Font setup
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

# Computer AI logic
def computer_ai():
    # Advanced AI: Move toward the shuttlecock with prediction and strategy
    target_x = shuttlecock.x
    
    # If shuttlecock is moving toward computer, predict landing spot
    if shuttlecock.vx > 0 and shuttlecock.x > NET_X:
        # Better prediction - adjust based on shuttlecock trajectory
        time_to_impact = (FLOOR_Y - shuttlecock.y) / max(0.1, shuttlecock.vy)
        target_x = shuttlecock.x + (shuttlecock.vx * time_to_impact)
        
        # Add strategic positioning
        if shuttlecock.y < HEIGHT * 0.3 and abs(shuttlecock.vy) > 5:
            # Prepare for smash - move back
            target_x = min(target_x, COURT_RIGHT - 100)
        elif shuttlecock.y > HEIGHT * 0.6:
            # Prepare for drop shot - move forward
            target_x = max(target_x, NET_X + 100)
    else:
        # Return to center when shuttlecock is on player's side
        target_x = (NET_X + COURT_RIGHT) / 2
    
    # Add some randomness to make AI imperfect but still challenging
    target_x += random.randint(-20, 20)
    
    # Move toward target
    if target_x < computer.x + computer.width / 2:
        computer.move("left")
    else:
        computer.move("right")
    
    # Jump logic - jump for high shuttlecocks
    if (shuttlecock.y < computer.y - 50 and 
        shuttlecock.x > NET_X and 
        abs(shuttlecock.x - computer.x) < 100 and
        computer.on_ground):
        computer.move("jump")
    
    # Decide whether to swing with improved timing
    if (shuttlecock.x > NET_X and  # Shuttlecock on computer's side
        abs(shuttlecock.x - (computer.x + computer.width / 2)) < 60 and  # Close horizontally
        abs(shuttlecock.y - (computer.y + computer.height / 3)) < 60):  # Close vertically
        
        # Better timing based on shuttlecock trajectory
        if shuttlecock.vy > 0 or abs(shuttlecock.y - computer.y) < 30:
            return computer.swing()
    return False

# Draw court
def draw_court():
    # Court background with gradient
    for y in range(COURT_TOP, COURT_BOTTOM):
        # Create a gradient from darker to lighter green
        color_value = 60 + int(30 * (y - COURT_TOP) / COURT_HEIGHT)
        court_color = (60, color_value, 113)
        pygame.draw.line(screen, court_color, (COURT_LEFT, y), (COURT_RIGHT, y))
    
    # Court border
    pygame.draw.rect(screen, COURT_LINES, (COURT_LEFT, COURT_TOP, COURT_WIDTH, COURT_HEIGHT), 3)
    
    # Net with texture
    net_rect = pygame.Rect(NET_X - NET_WIDTH // 2, NET_TOP, NET_WIDTH, NET_HEIGHT)
    pygame.draw.rect(screen, NET_COLOR, net_rect)
    
    # Net texture (horizontal lines)
    for y in range(NET_TOP, NET_TOP + NET_HEIGHT, 10):
        pygame.draw.line(screen, (180, 180, 180), (NET_X - NET_WIDTH // 2, y), 
                        (NET_X + NET_WIDTH // 2, y), 1)
    
    # Net post
    pygame.draw.rect(screen, (150, 75, 0), (NET_X - NET_WIDTH // 2 - 5, NET_TOP - 10, 10, NET_HEIGHT + 10))
    pygame.draw.rect(screen, (150, 75, 0), (NET_X + NET_WIDTH // 2 - 5, NET_TOP - 10, 10, NET_HEIGHT + 10))
    
    # Service lines
    service_y = COURT_TOP + COURT_HEIGHT // 3
    pygame.draw.line(screen, COURT_LINES, (COURT_LEFT, service_y), (COURT_RIGHT, service_y), 2)
    
    # Center line
    pygame.draw.line(screen, COURT_LINES, (NET_X, COURT_TOP), (NET_X, service_y), 2)
    
    # Service boxes
    mid_left = (COURT_LEFT + NET_X) // 2
    mid_right = (NET_X + COURT_RIGHT) // 2
    pygame.draw.line(screen, COURT_LINES, (mid_left, COURT_TOP), (mid_left, service_y), 1)
    pygame.draw.line(screen, COURT_LINES, (mid_right, COURT_TOP), (mid_right, service_y), 1)
    
    # Court markings for better visual reference
    for x in range(COURT_LEFT, COURT_RIGHT, 50):
        pygame.draw.line(screen, (70, 160, 120), (x, COURT_BOTTOM - 5), (x, COURT_BOTTOM), 1)
        
    # Draw shadows
    shadow_surface = pygame.Surface((COURT_WIDTH, 20), pygame.SRCALPHA)
    shadow_surface.fill((0, 0, 0, 30))
    screen.blit(shadow_surface, (COURT_LEFT, COURT_BOTTOM - 15))

# Draw scores and game info
def draw_ui():
    # Draw scores with better styling
    score_bg = pygame.Rect(10, 10, 180, 40)
    pygame.draw.rect(screen, (0, 0, 0, 128), score_bg, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), score_bg, 2, border_radius=10)
    
    computer_score_bg = pygame.Rect(WIDTH - 190, 10, 180, 40)
    pygame.draw.rect(screen, (0, 0, 0, 128), computer_score_bg, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), computer_score_bg, 2, border_radius=10)
    
    player_text = font.render(f"Player: {player_score}", True, TEXT_COLOR)
    computer_text = font.render(f"Computer: {computer_score}", True, TEXT_COLOR)
    screen.blit(player_text, (20, 15))
    screen.blit(computer_text, (WIDTH - 180, 15))
    
    # Draw game state messages
    if game_state == MENU:
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw title with shadow effect
        title_shadow = large_font.render("BADMINTON CHAMPIONSHIP", True, (0, 0, 0))
        title = large_font.render("BADMINTON CHAMPIONSHIP", True, (255, 215, 0))  # Gold color
        screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, HEIGHT // 3 + 3))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        
        # Draw animated start button
        button_width, button_height = 250, 60
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 2
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        # Draw button with pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5 + 5
        pygame.draw.rect(screen, button_color, (button_x - pulse/2, button_y - pulse/2, 
                                              button_width + pulse, button_height + pulse), 
                        border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), (button_x - pulse/2, button_y - pulse/2, 
                                                 button_width + pulse, button_height + pulse), 
                        3, border_radius=15)
        
        start_text = font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, button_y + button_height // 2 - start_text.get_height() // 2))
        
        # Draw instructions
        instructions = [
            "Controls:",
            "LEFT/RIGHT - Move player",
            "UP - Jump",
            "SPACE - Serve/Hit",
            "ESC - Quit game"
        ]
        
        for i, line in enumerate(instructions):
            instr_text = pygame.font.SysFont(None, 28).render(line, True, (200, 200, 200))
            screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT // 2 + 100 + i * 30))
    
    elif game_state == SERVE:
        # Draw serve indicator
        serve_bg = pygame.Rect(WIDTH // 2 - 200, 10, 400, 40)
        pygame.draw.rect(screen, (0, 0, 0, 150), serve_bg, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), serve_bg, 2, border_radius=10)
        
        if serving:
            serve_text = font.render("Player to Serve - Press SPACE", True, (255, 255, 255))
        else:
            serve_text = font.render("Computer to Serve", True, (255, 255, 255))
        screen.blit(serve_text, (WIDTH // 2 - serve_text.get_width() // 2, 15))
        
        # Draw arrow indicating serve direction
        if serving:
            arrow_start = (player.x + player.width + 10, player.y + player.height // 2)
            arrow_end = (arrow_start[0] + 50, arrow_start[1] - 30)
            pygame.draw.line(screen, (255, 255, 0), arrow_start, arrow_end, 3)
            pygame.draw.polygon(screen, (255, 255, 0), [
                (arrow_end[0], arrow_end[1]),
                (arrow_end[0] - 10, arrow_end[1] - 5),
                (arrow_end[0] - 5, arrow_end[1] + 10)
            ])
        else:
            arrow_start = (computer.x - 10, computer.y + computer.height // 2)
            arrow_end = (arrow_start[0] - 50, arrow_start[1] - 30)
            pygame.draw.line(screen, (255, 255, 0), arrow_start, arrow_end, 3)
            pygame.draw.polygon(screen, (255, 255, 0), [
                (arrow_end[0], arrow_end[1]),
                (arrow_end[0] + 10, arrow_end[1] - 5),
                (arrow_end[0] + 5, arrow_end[1] + 10)
            ])
    
    elif game_state == POINT_SCORED:
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # Draw point scored message with animation
        scale = 1 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1
        
        if serving:  # Player scored
            point_text = large_font.render("Player Scored!", True, (255, 215, 0))
        else:  # Computer scored
            point_text = large_font.render("Computer Scored!", True, (255, 215, 0))
            
        # Apply scaling to text
        scaled_text = pygame.transform.scale(point_text, 
                                           (int(point_text.get_width() * scale), 
                                            int(point_text.get_height() * scale)))
        
        screen.blit(scaled_text, (WIDTH // 2 - scaled_text.get_width() // 2, HEIGHT // 3))
        
        # Draw continue button
        button_width, button_height = 300, 50
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 2 + 50
        
        pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 2, border_radius=10)
        
        continue_text = font.render("Press SPACE to Continue", True, (255, 255, 255))
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, button_y + button_height // 2 - continue_text.get_height() // 2))
    
    elif game_state == GAME_OVER:
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw game over message with trophy icon
        if player_score > computer_score:
            winner_text = large_font.render("Player Wins!", True, (255, 215, 0))
            # Draw trophy
            trophy_x = WIDTH // 2
            trophy_y = HEIGHT // 3 - 80
            # Trophy cup
            pygame.draw.ellipse(screen, (255, 215, 0), (trophy_x - 40, trophy_y, 80, 40))
            pygame.draw.rect(screen, (255, 215, 0), (trophy_x - 30, trophy_y + 40, 60, 60))
            # Trophy handles
            pygame.draw.ellipse(screen, (255, 215, 0), (trophy_x - 60, trophy_y + 10, 30, 20))
            pygame.draw.ellipse(screen, (255, 215, 0), (trophy_x + 30, trophy_y + 10, 30, 20))
            # Trophy base
            pygame.draw.rect(screen, (255, 215, 0), (trophy_x - 20, trophy_y + 100, 40, 20))
            pygame.draw.rect(screen, (255, 215, 0), (trophy_x - 30, trophy_y + 120, 60, 10))
        else:
            winner_text = large_font.render("Computer Wins!", True, (255, 100, 100))
        
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 3))
        
        # Draw final score
        score_text = font.render(f"Final Score: Player {player_score} - {computer_score} Computer", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        
        # Draw restart button
        button_width, button_height = 200, 50
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 2 + 80
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=10)
        
        restart_text = font.render("Play Again (R)", True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, button_y + button_height // 2 - restart_text.get_height() // 2))

# Reset game
def reset_game():
    global game_state, player_score, computer_score, serving, rally_started
    player_score = 0
    computer_score = 0
    serving = True  # Player serves first
    rally_started = False
    game_state = SERVE
    shuttlecock.reset(True, serving)
    player.x = COURT_LEFT + 50
    computer.x = COURT_RIGHT - 50 - PLAYER_WIDTH

# Main game loop
clock = pygame.time.Clock()
running = True

# Add sound effects (commented out for now)
# try:
#     pygame.mixer.init()
#     hit_sound = pygame.mixer.Sound('hit.wav')
#     net_hit_sound = pygame.mixer.Sound('net_hit.wav')
#     point_sound = pygame.mixer.Sound('point.wav')
#     crowd_cheer = pygame.mixer.Sound('cheer.wav')
#     pygame.mixer.music.load('background_music.mp3')
#     pygame.mixer.music.set_volume(0.5)
#     pygame.mixer.music.play(-1)  # Loop background music
# except:
#     print("Sound files not found. Game will run without sound.")

# Particle system for visual effects
particles = []

# Function to add particles
def add_particles(x, y, color, count=10, speed=3, size_range=(2, 5)):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed_val = random.uniform(1, speed)
        size = random.randint(size_range[0], size_range[1])
        lifetime = random.randint(20, 60)  # Frames
        particles.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed_val,
            'vy': math.sin(angle) * speed_val,
            'size': size,
            'color': color,
            'lifetime': lifetime
        })

# Function to update and draw particles
def update_particles():
    to_remove = []
    for i, particle in enumerate(particles):
        # Update position
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        
        # Apply gravity and fade
        particle['vy'] += 0.1
        particle['lifetime'] -= 1
        
        # Draw particle
        alpha = min(255, int(255 * (particle['lifetime'] / 60)))
        color = list(particle['color'])
        if len(color) == 3:
            color.append(alpha)
        else:
            color[3] = alpha
            
        # Create surface with alpha
        particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
        screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Mark for removal if lifetime is over
        if particle['lifetime'] <= 0:
            to_remove.append(i)
    
    # Remove dead particles
    for i in sorted(to_remove, reverse=True):
        if i < len(particles):
            particles.pop(i)

# Game variables for visual effects
last_hit_pos = None
rally_count = 0  # Count consecutive hits
combo_display_time = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            if event.key == pygame.K_SPACE:
                if game_state == MENU:
                    game_state = SERVE
                    shuttlecock.reset(True, serving)
                
                elif game_state == SERVE:
                    if serving:  # Player's serve
                        rally_started = True
                        player.swing()
                        shuttlecock.hit(player, 8)  # Lighter hit for serve
                        last_hit_pos = (player.x + player.width, player.y + player.height // 2)
                        add_particles(last_hit_pos[0], last_hit_pos[1], (255, 165, 0), 15)
                    game_state = PLAYING
                
                elif game_state == POINT_SCORED:
                    game_state = SERVE
                    shuttlecock.reset(True, serving)
                    rally_count = 0  # Reset rally count
            
            if event.key == pygame.K_r and game_state == GAME_OVER:
                reset_game()
                rally_count = 0
            
            if event.key == pygame.K_UP and (game_state == PLAYING or game_state == SERVE):
                player.move("jump")
            
            if game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    # Player swing
                    if player.swing() and not player.is_computer:
                        # Check if player can hit the shuttlecock
                        if (shuttlecock.x < NET_X and  # Shuttlecock on player's side
                            abs(shuttlecock.x - (player.x + player.width)) < 60 and  # Close horizontally
                            abs(shuttlecock.y - (player.y + player.height / 2)) < 60):  # Close vertically
                            
                            shuttlecock.hit(player)
                            rally_started = True
                            rally_count += 1
                            last_hit_pos = (player.x + player.width, player.y + player.height // 2)
                            
                            # Add hit particles
                            if not player.on_ground:  # Jumping hit (smash)
                                add_particles(last_hit_pos[0], last_hit_pos[1], (255, 100, 0), 25, 5)
                            else:
                                add_particles(last_hit_pos[0], last_hit_pos[1], (255, 165, 0), 15)
                            
                            # Update combo display
                            if rally_count >= 3:
                                combo_display_time = 120  # Show for 2 seconds
        
        # Mouse click for buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Menu start button
            if game_state == MENU:
                button_width, button_height = 250, 60
                button_x = WIDTH // 2 - button_width // 2
                button_y = HEIGHT // 2
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                if button_rect.collidepoint(mouse_pos):
                    game_state = SERVE
                    shuttlecock.reset(True, serving)
            
            # Game over restart button
            elif game_state == GAME_OVER:
                button_width, button_height = 200, 50
                button_x = WIDTH // 2 - button_width // 2
                button_y = HEIGHT // 2 + 80
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                if button_rect.collidepoint(mouse_pos):
                    reset_game()
                    rally_count = 0
    
    # Get keyboard state for continuous movement
    keys = pygame.key.get_pressed()
    if game_state == PLAYING or game_state == SERVE:
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")
    
    # Game logic
    if game_state == PLAYING:
        # Update player and computer
        player.update()
        computer.update()
        
        # Computer AI
        if computer_ai() and shuttlecock.x > NET_X:
            # Check if computer can hit the shuttlecock
            if (abs(shuttlecock.x - computer.x) < 60 and  # Close horizontally
                abs(shuttlecock.y - (computer.y + computer.height / 2)) < 60):  # Close vertically
                
                shuttlecock.hit(computer)
                rally_count += 1
                last_hit_pos = (computer.x, computer.y + computer.height // 2)
                
                # Add hit particles
                if not computer.on_ground:  # Jumping hit
                    add_particles(last_hit_pos[0], last_hit_pos[1], (100, 100, 255), 20, 4)
                else:
                    add_particles(last_hit_pos[0], last_hit_pos[1], (150, 150, 255), 15)
                
                # Update combo display
                if rally_count >= 3:
                    combo_display_time = 120  # Show for 2 seconds
        
        # Update shuttlecock
        hit_floor = shuttlecock.update()
        
        # Check if shuttlecock hit the floor
        if hit_floor:
            # Add impact particles
            add_particles(shuttlecock.x, FLOOR_Y, (200, 200, 200), 30, 3)
            
            # Determine who scored
            if shuttlecock.x < NET_X:
                # Computer scores
                computer_score += 1
                serving = False  # Computer serves next
            else:
                # Player scores
                player_score += 1
                serving = True  # Player serves next
            
            game_state = POINT_SCORED
            
            # Check for game over
            if player_score >= winning_score or computer_score >= winning_score:
                game_state = GAME_OVER
    
    # Update combo display time
    if combo_display_time > 0:
        combo_display_time -= 1
    
    # Update particles
    update_particles()
    
    # Drawing
    screen.fill(BLACK)
    draw_court()
    
    # Draw players and shuttlecock
    player.draw()
    computer.draw()
    if game_state != MENU:
        shuttlecock.draw()
    
    # Draw rally combo
    if combo_display_time > 0 and rally_count >= 3:
        combo_text = font.render(f"{rally_count}x Rally!", True, (255, 215, 0))
        # Pulse effect
        scale = 1 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1
        combo_text = pygame.transform.scale(combo_text, 
                                          (int(combo_text.get_width() * scale), 
                                           int(combo_text.get_height() * scale)))
        screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, HEIGHT // 4))
    
    # Draw UI
    draw_ui()
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
