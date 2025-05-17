import pygame
import math

pygame.init()
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

center = (width // 2, height // 2)
radius = 150
num_points = 1

angle_step = math.radians(2)  # rotation step for Q/E keys on setpoint heading

# Spin variables
spin_angle = 0.0
spin_speed = 0.0  # radians per frame, adjustable with A/D
spin_speed_step = math.radians(0.5)  # how much spin_speed changes per key press
translate_power = 0.0

setpoint_heading = 0.0  # controlled with Q/E

def angle_diff(a, b):
    diff = a - b
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # Adjust setpoint heading with Q/E
    if keys[pygame.K_q]:
        setpoint_heading -= angle_step
    if keys[pygame.K_e]:
        setpoint_heading += angle_step
    setpoint_heading %= 2 * math.pi

    # Adjust spin speed and motor power with A/D and W/S
    if keys[pygame.K_a]:
        spin_speed -= spin_speed_step
    if keys[pygame.K_d]:
        spin_speed += spin_speed_step
    if keys[pygame.K_w]:
        translate_power = 100
    else:
        translate_power = 0

    # Update spin angle
    spin_angle += spin_speed
    spin_angle %= 2 * math.pi

    # Calculate points rotated by spin_angle
    point_angles = [(i * (2 * math.pi / num_points) + spin_angle) % (2 * math.pi) for i in range(num_points)]

    pygame.draw.circle(screen, (100, 100, 255), center, radius, 2)

    # Offset the heading by 180 degrees for vector calculation
    offset_heading = (setpoint_heading + math.pi) % (2 * math.pi)

    # Sum vector components for net force
    sum_fx = 0
    sum_fy = 0

    for angle in point_angles:
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)

        diff = angle_diff(angle, offset_heading)

        mag = math.sin(diff)
        if mag < 0:
            mag = 0  # one direction only

        tangent_angle = angle + math.pi / 2
        tx = math.cos(tangent_angle)
        ty = math.sin(tangent_angle)

        fx = mag * translate_power * tx
        fy = mag * translate_power * ty

        sum_fx += fx
        sum_fy += fy

        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 6)
        pygame.draw.line(screen, (255, 100, 100), (x, y), (x + fx, y + fy), 3)

    # Draw the net force vector from the center
    net_scale = 1.5  # scaling factor for display
    net_fx = sum_fx * net_scale
    net_fy = sum_fy * net_scale
    pygame.draw.line(screen, (100, 255, 100), center, (center[0] + net_fx, center[1] + net_fy), 5)
    pygame.draw.circle(screen, (100, 255, 100), (int(center[0] + net_fx), int(center[1] + net_fy)), 8)

    sp_x = center[0] + radius * math.cos(setpoint_heading)
    sp_y = center[1] + radius * math.sin(setpoint_heading)
    pygame.draw.line(screen, (255, 255, 0), center, (sp_x, sp_y), 3)

    text = font.render(
        f'Setpoint Heading: {math.degrees(setpoint_heading):.1f}°  |  Spin Speed: {math.degrees(spin_speed):.1f}°/frame',
        True, (200, 200, 200)
    )
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
