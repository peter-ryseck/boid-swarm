import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boids Simulation")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

NUM_BOIDS = 1000
MAX_SPEED = 20
MAX_FORCE = 0.2
MAX_FORCE_WALL = 0.25
NEIGHBOR_RADIUS = 0
AVOID_RADIUS = 50

class Boid:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

    def edges(self):
        margin = 50
        steer_force = pygame.math.Vector2(0, 0)

        if self.position.x < margin:
            steer_force.x = MAX_SPEED
        elif self.position.x > WIDTH - margin:
            steer_force.x = -MAX_SPEED
        if self.position.y < margin:
            steer_force.y = MAX_SPEED
        elif self.position.y > HEIGHT - margin:
            steer_force.y = -MAX_SPEED

        if steer_force.length() > 0:
            steer_force = (steer_force.normalize() * MAX_SPEED) - self.velocity
            steer_force = self.limit_force(steer_force, MAX_FORCE_WALL)

        self.velocity += steer_force

    def compute_behaviors(self, boids):
        align_sum = pygame.math.Vector2(0, 0)
        cohesion_sum = pygame.math.Vector2(0, 0)
        separation_sum = pygame.math.Vector2(0, 0)

        align_total = cohesion_total = separation_total = 0

        for boid in boids:
            if boid == self:
                continue

            distance = self.position.distance_to(boid.position)

            if distance < NEIGHBOR_RADIUS:
                align_sum += boid.velocity
                cohesion_sum += boid.position
                align_total += 1
                cohesion_total += 1

            if distance < AVOID_RADIUS and distance != 0:
                diff = self.position - boid.position
                diff /= distance
                separation_sum += diff
                separation_total += 1

        align_steering = self.calculate_steering(align_sum, align_total, normalize=True)
        cohesion_steering = self.calculate_steering(cohesion_sum, cohesion_total, subtract_pos=True)
        separation_steering = self.calculate_steering(separation_sum, separation_total, normalize=True)

        return align_steering, cohesion_steering, separation_steering

    def calculate_steering(self, vector_sum, total, normalize=False, subtract_pos=False):
        if total > 0:
            vector_sum /= total
            if subtract_pos:
                vector_sum -= self.position
            if normalize:
                vector_sum = (vector_sum.normalize() * MAX_SPEED)
            vector_sum -= self.velocity
            vector_sum = self.limit_force(vector_sum)
        return vector_sum

    def limit_force(self, force, max_force=MAX_FORCE):
        if force.length() > max_force:
            force.scale_to_length(max_force)
        return force

    def update(self, boids):
        align_force, cohesion_force, separation_force = self.compute_behaviors(boids)

        self.velocity += (
            align_force * MAX_FORCE +
            cohesion_force * MAX_FORCE +
            separation_force * MAX_FORCE
        )

        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity

    def draw(self):
        angle = self.velocity.angle_to(pygame.math.Vector2(1, 0))
        points = [
            (self.position.x + 10 * math.cos(math.radians(angle)),
             self.position.y + 10 * math.sin(math.radians(angle))),
            (self.position.x - 5 * math.cos(math.radians(angle + 140)),
             self.position.y - 5 * math.sin(math.radians(angle + 140))),
            (self.position.x - 5 * math.cos(math.radians(angle - 140)),
             self.position.y - 5 * math.sin(math.radians(angle - 140))),
        ]
        pygame.draw.polygon(screen, WHITE, points)


def main():
    clock = pygame.time.Clock()
    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        for boid in boids:
            boid.edges()
            boid.update(boids)
            boid.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
