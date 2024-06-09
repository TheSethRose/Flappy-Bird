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
SPAWN_PIPE = pygame.USEREVENT
PIPE_SPAWN_INTERVAL = 1200
POWER_UP_SIZE = 50

# Load game assets
background_image = pygame.image.load('assets/background.png')
bird_sprite = pygame.image.load('assets/bird.png')
pipe_sprite = pygame.image.load('assets/pipe.png')
logo_image = pygame.image.load('assets/logo.png')
ground_image = pygame.image.load('assets/ground.png')
game_over_image = pygame.image.load('assets/gameover.png')
power_up_image = pygame.image.load('assets/power_up.png')

# Scale the pipe sprite
pipe_sprite = pygame.transform.scale(pipe_sprite, (PIPE_WIDTH, PIPE_HEIGHT))

# Scale the ground sprite
GROUND_HEIGHT = ground_image.get_height() // 4
ground_image = pygame.transform.scale(ground_image, (ground_image.get_width(), GROUND_HEIGHT))

# Scale the power-up sprite
power_up_image = pygame.transform.scale(power_up_image, (POWER_UP_SIZE, POWER_UP_SIZE))

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

class Pipe(pygame.Rect):
    """Represents a pipe obstacle in the game."""
    def __init__(self, x, y, width, height):
        """Initializes a new Pipe object.

        Args:
            x: The x-coordinate of the top-left corner of the pipe.
            y: The y-coordinate of the top-left corner of the pipe.
            width: The width of the pipe.
            height: The height of the pipe.
        """
        super().__init__(x, y, width, height)
        self.passed = False

class PowerUp(pygame.Rect):
    """Represents a power-up item in the game."""
    def __init__(self, x, y, width, height):
        """Initializes a new PowerUp object.

        Args:
            x: The x-coordinate of the top-left corner of the power-up.
            y: The y-coordinate of the top-left corner of the power-up.
            width: The width of the power-up.
            height: The height of the power-up.
        """
        super().__init__(x, y, width, height)

def generate_pipe():
    """Generates a pair of pipes with a random gap position.

    Returns:
        A tuple containing the top pipe and bottom pipe.
    """
    pipe_height = random.randint(200, 400)
    top_pipe = Pipe(SCREEN_WIDTH + PIPE_WIDTH, pipe_height - PIPE_GAP // 2 - PIPE_HEIGHT, PIPE_WIDTH, PIPE_HEIGHT)
    bottom_pipe = Pipe(SCREEN_WIDTH + PIPE_WIDTH, pipe_height + PIPE_GAP // 2, PIPE_WIDTH, PIPE_HEIGHT)
    return top_pipe, bottom_pipe

def move_pipes(pipes):
    """Moves pipes to the left.

    Args:
        pipes: A list of pipe objects.

    Returns:
        The updated list of pipe objects.
    """
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    return pipes

def move_power_ups(power_ups):
    """Moves power-ups to the left.

    Args:
        power_ups: A list of power-up objects.

    Returns:
        The updated list of power-up objects.
    """
    for power_up in power_ups:
        power_up.centerx -= PIPE_SPEED
    return power_ups

def draw_pipes(pipes):
    """Draws pipes on the screen.

    Args:
        pipes: A list of pipe objects.
    """
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_sprite, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_sprite, False, True)
            screen.blit(flip_pipe, pipe)

def check_pipe_collision(pipes, bird_rect):
    """Checks for collisions between the bird and pipes.

    Args:
        pipes: A list of pipe objects.
        bird_rect: The Rect object representing the bird.

    Returns:
        True if a collision is detected, False otherwise.
    """
    return any(bird_rect.colliderect(pipe) for pipe in pipes)

def draw_text_background(rect, color=(0, 0, 0), alpha=128):
    """Draws a semi-transparent background rectangle.

    Args:
        rect: The Rect object representing the background rectangle.
        color: The color of the background rectangle (default black).
        alpha: The transparency of the background rectangle (default 128).
    """
    background_surface = pygame.Surface((rect.width + 10, rect.height + 10))  # Create a surface for the background
    background_surface.set_alpha(alpha)  # Set the transparency
    background_surface.fill(color)  # Fill the surface with the specified color
    screen.blit(background_surface, (rect.x - 5, rect.y - 5))  # Blit the background onto the screen

def display_game_over():
    """Displays the game over image in the center of the screen."""
    game_over_surface = pygame.transform.scale(game_over_image, (359, 100))
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    draw_text_background(game_over_rect)
    screen.blit(game_over_surface, game_over_rect)

def draw_ground(ground_x):
    """Draws the scrolling ground at the bottom of the screen.

    Args:
        ground_x: The x-coordinate of the ground.
    """
    for i in range((SCREEN_WIDTH // ground_image.get_width()) + 2):
        screen.blit(ground_image, (ground_x + i * ground_image.get_width(), SCREEN_HEIGHT - GROUND_HEIGHT + GROUND_Y_OFFSET))

def draw_menu(options, selected_index, title_surface=None, title_rect=None, bird_surface=None, bird_rect=None):
    """Draws a menu with options and highlights the selected option.

    Args:
        options: A list of menu options.
        selected_index: The index of the currently selected option.
        title_surface: The surface of the title image (optional).
        title_rect: The Rect object of the title image (optional).
        bird_surface: The surface of the bird image (optional).
        bird_rect: The Rect object of the bird image (optional).
    """
    if title_surface and title_rect:
        screen.blit(title_surface, title_rect)
    if bird_surface and bird_rect:
        screen.blit(bird_surface, bird_rect)

    font = pygame.font.Font(None, 36)
    menu_height = len(options) * 45
    background_rect = pygame.Rect(50, (SCREEN_HEIGHT / 2 - menu_height / 4), SCREEN_WIDTH - 100, menu_height)
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
    """Runs the menu loop, handling navigation and selection.

    Args:
        options: A list of menu options.
        title_surface: The surface of the title image (optional).

    Returns:
        The index of the selected option.
    """
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
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT / 2 - 150 + hover_offset))
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

def display_score(score):
    """Displays the current score on the screen with a black transparent box.

    Args:
        score: The current score.
    """
    font = pygame.font.Font(None, 36)
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    draw_text_background(score_rect, alpha=128)
    screen.blit(score_surface, score_rect)

def generate_power_up(pipes):
    """Generates a power-up item that doesn't collide with pipes.

    Args:
        pipes: A list of pipe objects.

    Returns:
        A Rect object representing the power-up.
    """
    while True:
        power_up_x = random.randint(100, SCREEN_WIDTH - 100)
        power_up_y = random.randint(100, SCREEN_HEIGHT - 100)
        power_up_rect = pygame.Rect(power_up_x, power_up_y, POWER_UP_SIZE, POWER_UP_SIZE)
        if not any(pipe.colliderect(power_up_rect) for pipe in pipes):
            return power_up_rect

def main_game():
    """Runs the main game loop."""
    global score
    clock = pygame.time.Clock()
    bird_y = BIRD_START_Y
    bird_velocity = 0
    pipes = []
    power_ups = []
    collected_power_ups = 0
    pygame.time.set_timer(SPAWN_PIPE, PIPE_SPAWN_INTERVAL)
    bird_alive = True
    score = 0
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
            if event.type == SPAWN_PIPE:
                pipes.extend(generate_pipe())
                if random.random() < 0.1:  # 10% chance to generate a power-up
                    power_ups.append(generate_power_up(pipes))

        if bird_alive:
            bird_velocity += GRAVITY
            bird_y += bird_velocity
            bird_rect = bird_sprite.get_rect(center=(BIRD_START_X, bird_y))

            bird_angle = min(max(bird_velocity * -3, -45), 45)
            rotated_bird = pygame.transform.rotate(bird_sprite, bird_angle)
            rotated_bird_rect = rotated_bird.get_rect(center=(BIRD_START_X, bird_y))

            pipes = move_pipes(pipes)
            power_ups = move_power_ups(power_ups) # Move power-ups

            for pipe in pipes:
                if pipe.centerx < BIRD_START_X and not pipe.passed:
                    score += 1 + collected_power_ups # Calculate score based on power-ups
                    pipe.passed = True

            screen.blit(background_image, (0, 0))
            draw_pipes(pipes)
            draw_ground(ground_x - 1)
            screen.blit(rotated_bird, rotated_bird_rect)
            display_score(score)

            ground_x -= GROUND_SPEED
            if ground_x <= -ground_image.get_width():
                ground_x = 0

            if check_pipe_collision(pipes, rotated_bird_rect) or bird_y < 0 or bird_y > SCREEN_HEIGHT - GROUND_HEIGHT + GROUND_Y_OFFSET:
                bird_alive = False
                display_game_over()
                selected_option = menu_loop(["Restart Game", "Quit Game"], title_surface=game_over_image)
                if selected_option == 0:
                    return main_game()
                elif selected_option == 1:
                    pygame.quit()
                    sys.exit()

            for power_up in power_ups[:]:  # Iterate over a copy of the list
                screen.blit(power_up_image, power_up)
                if rotated_bird_rect.colliderect(power_up):
                    collected_power_ups += 1
                    power_ups.remove(power_up)  # Remove the power-up after collision

        pygame.display.update()
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
