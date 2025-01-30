import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
BOID_COUNT = 20
FIRE_COUNT = 5
BOID_SPEED = 2.5
EXTINGUISH_RADIUS = 15  # Boids can extinguish fire within this range
WATER_CAPACITY = 3  # Boids can extinguish 3 "levels" of fire before refilling
FIRE_SHRINK_AMOUNT = 1  # Fire reduces when extinguished
HOME_BASE = (100, 100)  # Location of boid refill base

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 69, 0)
BLUE = (0, 191, 255)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boid Swarm Firefighting Simulation")
clock = pygame.time.Clock()


class Boid:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.target = None  # Target fire to extinguish
        self.water = WATER_CAPACITY  # Start with full water
        self.returning_to_base = False

    def update(self, fires):
        if self.returning_to_base:
            # Go to home base if out of water
            self.move_towards(HOME_BASE)
            if self.distance_to_point(HOME_BASE) < 10:
                self.water = WATER_CAPACITY
                self.returning_to_base = False
        else:
            # Find the largest fire if we still have water
            if self.water > 0 and fires:
                self.target = max(fires, key=lambda f: f.size)

            if self.target:
                self.move_towards((self.target.x, self.target.y))

                # Extinguish fire if close enough
                if self.distance_to(self.target) < EXTINGUISH_RADIUS:
                    self.target.size -= FIRE_SHRINK_AMOUNT
                    self.water -= 1
                    if self.water == 0:
                        self.returning_to_base = True  # Go refill

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def move_towards(self, target):
        tx, ty = target
        angle = math.atan2(ty - self.y, tx - self.x)
        self.vx = math.cos(angle) * BOID_SPEED
        self.vy = math.sin(angle) * BOID_SPEED
        self.x += self.vx
        self.y += self.vy

    def distance_to(self, obj):
        return math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)

    def distance_to_point(self, point):
        px, py = point
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)

    def draw(self):
        pygame.draw.circle(screen, BLUE if self.water > 0 else GRAY, (int(self.x), int(self.y)), 5)


class Fire:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.size = random.randint(20, 40)  # Bigger fires

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)


# Initialize boids and fires
boids = [Boid() for _ in range(BOID_COUNT)]
fires = [Fire() for _ in range(FIRE_COUNT)]

running = True
while running:
    screen.fill(GREEN)  # Background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update boids
    for boid in boids:
        boid.update(fires)

    # Remove fires if they are completely extinguished
    fires = [fire for fire in fires if fire.size > 0]

    # Draw home base
    pygame.draw.circle(screen, WHITE, HOME_BASE, 10)

    # Draw fires
    for fire in fires:
        fire.draw()

    # Draw boids
    for boid in boids:
        boid.draw()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()