import numpy as np
import pygame
from scipy.optimize import minimize

# Constants
BOX_SIZE = 600  # pixels
WORLD_SIZE = 10.0  # meters (box is 10x10)
SCALE = BOX_SIZE / WORLD_SIZE
sensor_angles = np.deg2rad([0, 120, -120])  # relative to robot heading

# Ray-box intersection
def ray_box_intersection(x, y, angle, L):
    dx = np.cos(angle)
    dy = np.sin(angle)
    t_vals = []
    if dx != 0:
        t_vals += [t for t in [(0 - x) / dx, (L - x) / dx] if t > 0]
    if dy != 0:
        t_vals += [t for t in [(0 - y) / dy, (L - y) / dy] if t > 0]
    return min(t_vals) if t_vals else np.inf

# Simulate sensor readings with noise
def simulate_readings(x, y, theta, L):
    readings = [ray_box_intersection(x, y, theta + a, L) for a in sensor_angles]
    noise = np.random.normal(0, 0.01, 3)  # 1 cm noise
    return np.clip(np.array(readings) + noise, 0, L)

# Residual from wall distance
def wall_distance_residual(px, py, L):
    return min(abs(px - 0), abs(px - L), abs(py - 0), abs(py - L))

# Error to minimize
def objective(pose, distances, L):
    x, y, theta = pose
    error = 0
    for d, a in zip(distances, sensor_angles):
        px = x + d * np.cos(theta + a)
        py = y + d * np.sin(theta + a)
        error += wall_distance_residual(px, py, L)**2
    return error

# Estimate pose via optimization
def estimate_pose(distances, L):
    initial_guess = [L/2, L/2, 0.0]
    bounds = [(0, L), (0, L), (0, 2*np.pi)]
    result = minimize(objective, initial_guess, args=(distances, L), bounds=bounds)
    return result.x

# Convert world to screen
def world_to_screen(x, y):
    return int(x * SCALE), int(BOX_SIZE - y * SCALE)

# Draw the robot and sensor rays
def draw_robot(screen, x, y, theta, color, distances, label=False):
    cx, cy = world_to_screen(x, y)
    pygame.draw.circle(screen, color, (cx, cy), 6)
    for d, a in zip(distances, sensor_angles):
        angle = theta + a
        ex, ey = world_to_screen(x + d * np.cos(angle), y + d * np.sin(angle))
        pygame.draw.line(screen, color, (cx, cy), (ex, ey), 2)
    if label:
        font = pygame.font.SysFont(None, 18)
        label_text = font.render("True Pose", True, color)
        screen.blit(label_text, (cx + 10, cy - 10))

# Main simulation loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((BOX_SIZE + 100, BOX_SIZE + 50))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    # Initial robot state
    true_x, true_y, true_theta = 6.0, 3.0, np.deg2rad(30)
    dx, dy, dtheta = 0.02, 0.015, np.deg2rad(2)

    running = True
    while running:
        screen.fill((255, 255, 255))

        # Draw grid and labels
        for i in range(11):
            label = font.render(f"{i}", True, (0, 0, 0))
            x, y = i * SCALE, BOX_SIZE - i * SCALE
            screen.blit(label, (x - 5, BOX_SIZE + 5))
            screen.blit(label, (BOX_SIZE + 10, y - 5))
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, BOX_SIZE), 1)
            pygame.draw.line(screen, (200, 200, 200), (0, y), (BOX_SIZE, y), 1)

        pygame.draw.rect(screen, (0, 0, 0), (0, 0, BOX_SIZE, BOX_SIZE), 2)

        # Simulate and estimate
        distances = simulate_readings(true_x, true_y, true_theta, WORLD_SIZE)
        est_x, est_y, est_theta = estimate_pose(distances, WORLD_SIZE)

        # Draw true and estimated pose
        draw_robot(screen, true_x, true_y, true_theta, (0, 150, 0), distances, label=True)
        draw_robot(screen, est_x, est_y, est_theta, (200, 0, 0), distances)

        # Draw legend
        pygame.draw.rect(screen, (255, 255, 255), (BOX_SIZE + 10, 10, 80, 50))
        pygame.draw.circle(screen, (0, 150, 0), (BOX_SIZE + 20, 25), 6)
        pygame.draw.circle(screen, (200, 0, 0), (BOX_SIZE + 20, 45), 6)
        screen.blit(font.render("True", True, (0, 0, 0)), (BOX_SIZE + 35, 20))
        screen.blit(font.render("Estimated", True, (0, 0, 0)), (BOX_SIZE + 35, 40))

        # Move robot
        true_x += dx
        true_y += dy
        true_theta += dtheta
        if not (0.5 < true_x < 9.5): dx = -dx
        if not (0.5 < true_y < 9.5): dy = -dy

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
