def compute_behaviors(self, boids):
    # Initialize sums and counters
    align_sum_x = align_sum_y = 0
    cohesion_sum_x = cohesion_sum_y = 0
    separation_sum_x = separation_sum_y = 0
    align_total = cohesion_total = separation_total = 0

    for boid in boids:
        if boid == self:
            continue

        # Calculate distance using Pythagoras
        dx = self.position[0] - boid.position[0]
        dy = self.position[1] - boid.position[1]
        distance = (dx**2 + dy**2) ** 0.5

        if distance < NEIGHBOR_RADIUS:
            align_sum_x += boid.velocity[0]
            align_sum_y += boid.velocity[1]
            cohesion_sum_x += boid.position[0]
            cohesion_sum_y += boid.position[1]
            align_total += 1
            cohesion_total += 1

        if distance < AVOID_RADIUS and distance != 0:  # Avoid division by zero
            diff_x = dx / distance
            diff_y = dy / distance
            separation_sum_x += diff_x
            separation_sum_y += diff_y
            separation_total += 1

    # Calculate steering values
    align_steering = self.calculate_steering((align_sum_x, align_sum_y), align_total, normalize=True)
    cohesion_steering = self.calculate_steering((cohesion_sum_x, cohesion_sum_y), cohesion_total, subtract_pos=True)
    separation_steering = self.calculate_steering((separation_sum_x, separation_sum_y), separation_total, normalize=True)

    return align_steering, cohesion_steering, separation_steering