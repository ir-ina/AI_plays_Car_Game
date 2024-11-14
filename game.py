import pygame
import random
import numpy as np

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
ORANGE = (255, 0, 0)
CAR_COLOR = (100, 65, 20)

# Initialize Pygame
pygame.init()


# Class representing the car
class Car:
    def __init__(self, x=0, y=0, dx=4, dy=0, width=30, height=30, color=ORANGE):
        self.image = ""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.color = color

    # Load an image for the car
    def load_image(self, img):
        self.image = pygame.image.load(img).convert()
        self.image.set_colorkey(BLACK)

    def draw_image(self, screen):
        screen.blit(self.image, [self.x, self.y])

    def move_x(self):
        self.x += self.dx

    def move_y(self):
        self.y += self.dy

    # Draw a rectangle as the car (if no image)
    def draw_rect(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, self.width, self.height], 0)

    # Check if the car is out of screen bounds and adjust position
    def check_out_of_screen(self):
        if self.x + self.width > 400 or self.x < 0:
            self.x -= self.dx


# Main game class
class CarGameAI:
    def __init__(self):
        self.size = (400, 700)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Ride the Road")
        self.clock = pygame.time.Clock()  # Control game framerate
        self.font_30 = pygame.font.SysFont("Arial", 30, True, False)
        self.reward = 0
        self.reset()

    def reset(self):
        self.player = Car(165, 570, 0, 0, 70, 130, ORANGE)  # Create the player's car
        self.player.load_image("player.png")
        self.score = 0
        self.car = Car(random.randrange(0, 340), random.randrange(-150, -50), 0, 4, 60, 60,
                       CAR_COLOR)  # Create the obstacle car
        self.game_over = False

    # Update the obstacle car's position
    def update_car(self):
        self.car.draw_rect(self.screen)
        self.car.move_y()
        if self.car.y > self.size[1]:  # If the car is off the screen
            self.score += 10
            self.reward = 20  # Main reward
            self.car.y = random.randrange(-150, -50)
            self.car.x = random.randrange(0, 340)
            self.car.dy = 4

    def check_collision(self):
        if (
                self.player.x + self.player.width > self.car.x
                and self.player.x < self.car.x + self.car.width
                and self.player.y < self.car.y + self.car.height
                and self.player.y + self.player.height > self.car.y
        ):
            return True  # Collision detected
        return False

    # Main game loop
    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Process actions: left, right, or stay
        if np.array_equal(action, [1, 0, 0]):  # Move left
            self.player.dx = -4
            if self.car.x + self.car.width >= 399 - self.player.width and self.player.x + self.player.width >= self.car.x:
                self.reward = 10  # Reward for safe movement
            if self.player.x <= 3:  # If player is too far left
                self.reward += -2

        elif np.array_equal(action, [0, 1, 0]):  # Move right
            self.player.dx = 4
            if self.car.x <= 1 + self.player.width and self.player.x <= self.car.x + self.car.width:
                self.reward = 10  # Reward for safe movement
            if self.player.x + self.player.width >= 397:  # If player is too far right
                self.reward += -2

        else:  # No movement
            self.player.dx = 0
            if self.car.x + self.car.width > self.player.x and self.car.x < self.player.x + self.player.width:
                self.reward = -10  # Penalty for being in danger zone
            else:
                self.reward = 10  # Reward for staying safe

        # Update game display and state
        self.screen.fill(GRAY)
        self.player.draw_image(self.screen)
        self.player.move_x()
        self.player.check_out_of_screen()
        self.update_car()

        # Check for collisions
        if self.check_collision():
            self.game_over = True
            self.reward = -20  # Main penalty
            return self.reward, self.game_over, self.score

        # Display the score on the screen
        txt_score = self.font_30.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(txt_score, [15, 15])

        pygame.display.flip()  # Update display
        self.clock.tick(400)  # Limit game speed
        return self.reward, self.game_over, self.score
