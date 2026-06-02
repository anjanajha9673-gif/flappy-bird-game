import pygame
import random
import sys

# Pygame ko initialize karein
pygame.init()

# Mobile ki screen size automatic lene ke liye (Full Screen)
info = pygame.display.Info()
WIDTH = info.current_w if info.current_w > 0 else 400
HEIGHT = info.current_h if info.current_h > 0 else 600

if HEIGHT < 500:
    HEIGHT = 650 

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krish ka Ultra Real Flappy Bird")

# --- RANG (COLORS) ---
SKY_BLUE = (173, 216, 230)
NIGHT_BLUE = (15, 25, 45)      # 100 score ke baad ka rang
WHITE = (255, 255, 255)
CLOUD_COLOR = (255, 255, 255)

# Pedon ke liye realistic shades
DARK_GREEN = (25, 85, 25)     
LEAF_MEDIUM = (34, 120, 34)   
LEAF_LIGHT = (50, 165, 50)     
TRUNK_BROWN = (90, 55, 25)    

# Zameen ke do rang
SOIL_BROWN = (120, 75, 40)    
GRASS_GREEN = (40, 180, 40)   

BIRD_YELLOW = (245, 210, 50)   
BIRD_BEAK = (245, 90, 40)      
BIRD_WING = (245, 245, 220)    

PIPE_COLOR = (34, 177, 76)
PIPE_BORDER = (15, 90, 40)
BUILDING_COLOR = (120, 130, 140)

# --- GAME VARIABLES ---
GROUND_HEIGHT = int(HEIGHT * 0.82)
GRASS_THICKNESS = 18  

bird_x = int(WIDTH * 0.25)
bird_y = int(HEIGHT * 0.4)
bird_w = 54  
bird_h = 42  

gravity = 0.42       
lift = -8.5
velocity = 0

pipe_width = int(WIDTH * 0.18)
pipe_gap = int(HEIGHT * 0.19) 
base_pipe_speed = 5.0     # Default speed

pipes = [] 
score = 0
high_score = 17      
game_over = False

clock = pygame.time.Clock()

# Fonts
font_score = pygame.font.SysFont("Arial", 35, bold=True)
font_msg = pygame.font.SysFont("Arial", 28, bold=True)

# Scenery Objects
clouds = [[50, 140], [250, 110], [450, 160]]
buildings = [
    [10, GROUND_HEIGHT-380, 110, 380], 
    [150, GROUND_HEIGHT-450, 130, 450], 
    [320, GROUND_HEIGHT-350, 120, 350], 
    [480, GROUND_HEIGHT-400, 110, 400]
]
trees = [[80, GROUND_HEIGHT], [240, GROUND_HEIGHT], [400, GROUND_HEIGHT], [560, GROUND_HEIGHT]]

next_pipe_frame = 100
frame_counter = 0

def reset_game():
    global bird_y, velocity, pipes, score, game_over, frame_counter, next_pipe_frame
    bird_y = int(HEIGHT * 0.4)
    velocity = 0
    pipes = []
    score = 0
    frame_counter = 0
    next_pipe_frame = 60
    game_over = False

def draw_real_bird(x, y):
    pygame.draw.ellipse(screen, BIRD_YELLOW, (x - bird_w//2, y - bird_h//2, bird_w, bird_h))
    pygame.draw.ellipse(screen, (0, 0, 0), (x - bird_w//2, y - bird_h//2, bird_w, bird_h), 3)
    
    pygame.draw.circle(screen, WHITE, (x + 10, y - 10), 12)        
    pygame.draw.circle(screen, (0, 0, 0), (x + 10, y - 10), 12, 3) 
    pygame.draw.circle(screen, (0, 0, 0), (x + 12, y - 10), 4)     
    
    pygame.draw.ellipse(screen, BIRD_BEAK, (x + 14, y - 5, 24, 13))
    pygame.draw.ellipse(screen, (0, 0, 0), (x + 14, y - 5, 24, 13), 3) 
    
    pygame.draw.ellipse(screen, BIRD_BEAK, (x + 10, y + 4, 20, 11))
    pygame.draw.ellipse(screen, (0, 0, 0), (x + 10, y + 4, 20, 11), 3) 

    pygame.draw.ellipse(screen, BIRD_WING, (x - 20, y - 2, 22, 14))
    pygame.draw.ellipse(screen, (0, 0, 0), (x - 20, y - 2, 22, 14), 3)

def draw_real_pipe(x, top_h, bot_h, color, border_color):
    # Top Pipe
    pygame.draw.rect(screen, color, (x, 0, pipe_width, top_h))
    pygame.draw.rect(screen, border_color, (x, 0, pipe_width, top_h), 4)
    pygame.draw.rect(screen, border_color, (x - 4, top_h - 25, pipe_width + 8, 25))
    
    # Bottom Pipe
    pygame.draw.rect(screen, color, (x, HEIGHT - bot_h, pipe_width, bot_h))
    pygame.draw.rect(screen, border_color, (x, HEIGHT - bot_h, pipe_width, bot_h), 4)
    pygame.draw.rect(screen, border_color, (x - 4, HEIGHT - bot_h, pipe_width + 8, 25))

# --- MAIN LOOP ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reset_game()
            else:
                velocity = lift

    # --- SCORE KE JADU SE COLORS AUR RULES CHANGE KARNA ---
    current_sky_color = SKY_BLUE
    current_pipe_color = PIPE_COLOR
    current_pipe_border = PIPE_BORDER
    current_speed = base_pipe_speed

    # Rule 1: 50+ score par difficulty increase
    if score >= 50:
        current_speed = 6.8  # Speed tez ho gayi
        
    # Rule 2: 100+ score par Night Mode aur alag colors
    if score >= 100:
        current_sky_color = NIGHT_BLUE
        current_pipe_color = (230, 90, 40)    # Khambon ka rang neon orange
        current_pipe_border = (120, 30, 10)
        current_speed = 7.5                   # Extreme Speed!

    # Background Drawing
    screen.fill(current_sky_color)

    # Scenery Animations
    if not game_over:
        for c in clouds:
            c[0] -= 0.5
            if c[0] < -120: c[0] = WIDTH + 50
            
        for b in buildings:
            b[0] -= 1
            if b[0] < -150: b[0] = WIDTH + 20
            
        for t in trees:
            t[0] -= 2
            if t[0] < -100: t[0] = WIDTH + 50

    # Draw Clouds (Night mode mein thode light gray dikhenge)
    cloud_draw_color = WHITE if score < 100 else (130, 140, 160)
    for cx, cy in clouds:
        pygame.draw.circle(screen, cloud_draw_color, (int(cx), cy), 35)
        pygame.draw.circle(screen, cloud_draw_color, (int(cx) + 30, cy - 10), 40)
        pygame.draw.circle(screen, cloud_draw_color, (int(cx) + 60, cy), 35)

    # Draw Buildings
    for bx, by, bw, bh in buildings:
        pygame.draw.rect(screen, BUILDING_COLOR, (int(bx), by, bw, bh))
        window_color = WHITE if score < 100 else (255, 230, 150) # Raat mein light jalegi
        for wx in range(int(bx) + 20, int(bx) + bw - 15, 30):
            for wy in range(by + 30, GROUND_HEIGHT - 20, 50):
                pygame.draw.rect(screen, window_color, (wx, wy, 12, 18))

    # Draw Trees
    for tx, ty in trees:
        pygame.draw.rect(screen, TRUNK_BROWN, (int(tx) - 10, ty - 75, 20, 75)) 
        pygame.draw.circle(screen, DARK_GREEN, (int(tx), ty - 75), 45)
        pygame.draw.circle(screen, LEAF_MEDIUM, (int(tx), ty - 95), 35)
        pygame.draw.circle(screen, LEAF_LIGHT, (int(tx), ty - 110), 25)

    # Draw Ground
    pygame.draw.rect(screen, SOIL_BROWN, (0, GROUND_HEIGHT, WIDTH, HEIGHT - GROUND_HEIGHT))
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_HEIGHT, WIDTH, GRASS_THICKNESS))

    if not game_over:
        # Bird Physics
        velocity += gravity
        bird_y += int(velocity)

        if bird_y + bird_h//2 >= GROUND_HEIGHT or bird_y - bird_h//2 <= 0:
            game_over = True

        # --- DYNAMIC RANDOM SPAWN LOGIC ---
        frame_counter += 1
        # 50 score ke baad pipes thodi jaldi aayengi (35-70 frames ka gap)
        spawn_rate = random.randint(55, 120) if score < 50 else random.randint(35, 75)
        
        if frame_counter >= next_pipe_frame:
            min_h = int(HEIGHT * 0.12)
            max_h = int(HEIGHT * 0.45)
            top_height = random.randint(min_h, max_h)
            bottom_height = HEIGHT - (top_height + pipe_gap)
            
            # [x, top_h, bot_h, passed_flag, vertical_direction]
            # 100 ke baad pipelines upar neeche hilengi (1 means down, -1 means up)
            direction = random.choice([1, -1]) if score >= 100 else 0
            pipes.append([WIDTH, top_height, bottom_height, False, direction])
            
            frame_counter = 0
            next_pipe_frame = spawn_rate

    # Hitbox
    bird_rect = pygame.Rect(bird_x - bird_w//2, bird_y - bird_h//2, bird_w, bird_h)

    # Pipes Update
    for pipe in pipes[:]:
        if not game_over:
            pipe[0] -= current_speed
            
            # DYNAMIC PIPES EXTRA LOGIC (100+ Score Only)
            if score >= 100:
                pipe[1] += pipe[4] * 1.5 # Upar wali pipe sarak rahi hai
                pipe[2] -= pipe[4] * 1.5 # Neeche wali pipe sarak rahi hai
                # Agar pipe zyada badi ya choti ho jaye toh direction palat do
                if pipe[1] < int(HEIGHT * 0.08) or pipe[1] > int(HEIGHT * 0.55):
                    pipe[4] *= -1
        
        draw_real_pipe(pipe[0], pipe[1], pipe[2], current_pipe_color, current_pipe_border)

        top_pipe_rect = pygame.Rect(pipe[0], 0, pipe_width, pipe[1])
        bottom_pipe_rect = pygame.Rect(pipe[0], HEIGHT - pipe[2], pipe_width, pipe[2])

        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            game_over = True

        if pipe[0] + pipe_width < bird_x and not pipe[3]:
            score += 1
            pipe[3] = True
            if score > high_score:
                high_score = score

        if pipe[0] + pipe_width < 0:
            pipes.remove(pipe)

    # Draw Player
    draw_real_bird(bird_x, bird_y)

    # Score Panel
    score_text = font_score.render(f"Score: {score}", True, WHITE)
    hs_text = font_score.render(f"Best: {high_score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(hs_text, (WIDTH - 150, 20))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        go_text = font_score.render("GAME OVER", True, (255, 50, 50))
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(go_text, go_rect)

        restart_text = font_msg.render("Tap to Play Again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)
