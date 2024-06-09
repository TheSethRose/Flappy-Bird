import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BIRD_START_X = 100
BIRD_START_Y = 300
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 200
GRAVITY = 0.5
BIRD_FLAP_VELOCITY = -7
PIPE_SPEED = 5
GROUND_SPEED = 5
GROUND_Y_OFFSET = 25
SPAWNPIPE = pygame.USEREVENT
PIPE_SPAWN_INTERVAL = 1200

# Load game assets
background_image = pygame.image.load('assets/background.png')
bird_sprite = pygame.image.load('assets/bird.png')
pipe_sprite = pygame.image.load('assets/pipe.png')
logo_image = pygame.image.load('assets/logo.png')
ground_image = pygame.image.load('assets/ground.png')
game_over_image = pygame.image.load('assets/gameover.png')

# Scale the pipe sprite
pipe_sprite = pygame.transform.scale(pipe_sprite, (PIPE_WIDTH, PIPE_HEIGHT))

# Scale the ground sprite
GROUND_HEIGHT = ground_image.get_height() // 4
ground_image = pygame.transform.scale(ground_image, (ground_image.get_width(), GROUND_HEIGHT))

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

def generate_pipe():
    """Generate a pair of pipes with a random gap position."""
    pipe_height = random.randint(200, 400)
    top_pipe = pipe_sprite.get_rect(midbottom=(SCREEN_WIDTH + PIPE_WIDTH, pipe_height - PIPE_GAP // 2))
    bottom_pipe = pipe_sprite.get_rect(midtop=(SCREEN_WIDTH + PIPE_WIDTH, pipe_height + PIPE_GAP // 2))
    return top_pipe, bottom_pipe

def move_pipes(pipes):
    """Move pipes to the left."""
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    return pipes

def draw_pipes(pipes):
    """Draw pipes on the screen."""
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_sprite, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_sprite, False, True)
            screen.blit(flip_pipe, pipe)

def check_pipe_collision(pipes, bird_rect):
    """Check for collisions between the bird and pipes."""
    return any(bird_rect.colliderect(pipe) for pipe in pipes)

def draw_text_background(rect, color=(0, 0, 0), alpha=128):
    """Draw a semi-transparent background rectangle covering the entire message area."""
    background_rect = pygame.Rect(0, rect.top - 20, SCREEN_WIDTH, rect.height + 80)
    s = pygame.Surface((background_rect.width, background_rect.height))
    s.set_alpha(alpha)
    s.fill(color)
    screen.blit(s, background_rect.topleft)

def display_game_over():
    """Display the game over image in the center of the screen."""
    game_over_surface = pygame.transform.scale(game_over_image, (359, 100))
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
    draw_text_background(game_over_rect)
    screen.blit(game_over_surface, game_over_rect)

def draw_ground(ground_x):
    """Draw the scrolling ground at the bottom of the screen."""
    for i in range((SCREEN_WIDTH // ground_image.get_width()) + 2):
        screen.blit(ground_image, (ground_x + i * ground_image.get_width(), SCREEN_HEIGHT - GROUND_HEIGHT + GROUND_Y_OFFSET))

def draw_menu(options, selected_index, title_surface=None, title_rect=None, bird_surface=None, bird_rect=None):
    """Draw a menu with options and highlight the selected option."""
    if title_surface and title_rect:
        screen.blit(title_surface, title_rect)
    if bird_surface and bird_rect:
        screen.blit(bird_surface, bird_rect)

    font = pygame.font.Font(None, 36)
    menu_height = len(options) * 40
    background_rect = pygame.Rect(50, (SCREEN_HEIGHT / 2 - menu_height / 2), SCREEN_WIDTH - 100, menu_height)
    draw_text_background(background_rect, alpha=150)

    for i, option in enumerate(options):
        text_surface = font.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 40))
        screen.blit(text_surface, text_rect)
        if i == selected_index:
            arrow_surface = font.render(">", True, (255, 255, 255))
            arrow_rect = arrow_surface.get_rect(center=(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + i * 40))
            screen.blit(arrow_surface, arrow_rect)

def menu_loop(options, title_surface=None):
    """Menu loop to handle navigation and selection."""
    selected_option = 0
    menu_running = True
    clock = pygame.time.Clock()
    time = 0

    ground_x = 0

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected_option

        time += clock.get_time()
        hover_offset = math.sin(time * 0.005) * 10

        if title_surface is not None:
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150 + hover_offset))
            screen.blit(title_surface, title_rect)

        bird_angle = math.sin(time * 0.005) * 15
        rotated_bird = pygame.transform.rotate(bird_sprite, bird_angle)
        bird_rect = rotated_bird.get_rect(center=(SCREEN_WIDTH / 2 + 80, SCREEN_HEIGHT / 2 - 205 + hover_offset))

        screen.blit(background_image, (0, 0))
        draw_menu(options, selected_option, title_surface, title_rect, rotated_bird, bird_rect)
        draw_ground(ground_x)
        ground_x -= GROUND_SPEED
        if ground_x <= -ground_image.get_width():
            ground_x = 0
        pygame.display.flip()
        clock.tick(30)

def main_game():
    """Main game loop."""
    clock = pygame.time.Clock()
    bird_y = BIRD_START_Y
    bird_velocity = 0
    pipes = []
    pygame.time.set_timer(SPAWNPIPE, PIPE_SPAWN_INTERVAL)
    bird_alive = True

    ground_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if bird_alive and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = BIRD_FLAP_VELOCITY
            if event.type == SPAWNPIPE:
                pipes.extend(generate_pipe())

        if bird_alive:
            bird_velocity += GRAVITY
            bird_y += bird_velocity
            bird_rect = bird_sprite.get_rect(center=(BIRD_START_X, bird_y))

            bird_angle = min(max(bird_velocity * -3, -45), 45)
            rotated_bird = pygame.transform.rotate(bird_sprite, bird_angle)
            rotated_bird_rect = rotated_bird.get_rect(center=(BIRD_START_X, bird_y))

            pipes = move_pipes(pipes)

            screen.blit(background_image, (0, 0))
            draw_pipes(pipes)
            draw_ground(ground_x - 1)
            screen.blit(rotated_bird, rotated_bird_rect)
            ground_x -= GROUND_SPEED
            if ground_x <= -ground_image.get_width():
                ground_x = 0
            pygame.display.update()

            if check_pipe_collision(pipes, rotated_bird_rect) or bird_y < 0 or bird_y > SCREEN_HEIGHT - GROUND_HEIGHT + GROUND_Y_OFFSET:
                bird_alive = False
                display_game_over()
                selected_option = menu_loop(["Restart Game", "Quit Game"], title_surface=game_over_image)
                if selected_option == 0:
                    return main_game()
                elif selected_option == 1:
                    pygame.quit()
                    sys.exit()

        clock.tick(30)

if __name__ == "__main__":
    clock = pygame.time.Clock()
    logo_surface = pygame.transform.scale(logo_image, (300, 100))
    selected_option = menu_loop(["Start Game", "Quit Game"], title_surface=logo_surface)
    if selected_option == 0:
        main_game()
    elif selected_option == 1:
        pygame.quit()
        sys.exit()
