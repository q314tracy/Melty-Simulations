import pygame
import math

# window instance settings
pygame.init()
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# circle settings
center = (width // 2, height // 2)
radius = 150
num_points = 5

# global variables
spin_angle = 0.0
spin_speed = 0.01 * math.pi
spin_speed_step = math.radians(0.5)
translate_vector_x = 0.0
translate_vector_y = 0.0
translate_power = 0.0
setpoint_heading = 0.0

def angle_diff(a, b):
    diff = a - b
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

def draw_torque_arc(surface, center, torque, min_radius=20, max_radius=60):
    # Clamp torque magnitude for scaling
    torque_mag = min(abs(torque), 5000)  # adjust max torque for scaling

    # Map torque magnitude to radius size
    radius = min_radius + (max_radius - min_radius) * (torque_mag / 5000)

    # Map torque magnitude to arc length (max 270 degrees)
    max_arc = math.pi * 1.5  # 270 degrees in radians
    arc_length = min(torque_mag * 0.0006, max_arc)  # adjust sensitivity

    if arc_length < 0.05:
        # Arc too small to see, skip drawing
        return

    start_angle = -math.pi / 2  # start at top (12 o'clock)

    # Determine arc direction based on torque sign
    if torque > 0:
        end_angle = start_angle + arc_length  # clockwise arc
    else:
        end_angle = start_angle - arc_length  # counter-clockwise arc

    rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

    # Draw arc with thickness 6
    pygame.draw.arc(surface, (255, 255, 0), rect, min(start_angle, end_angle), max(start_angle, end_angle), 6)


# main loop
running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        translate_vector_x = 1
    elif keys[pygame.K_s]:
        translate_vector_x = -1
    else:
        translate_vector_x = 0

    if keys[pygame.K_d]:
        translate_vector_y = 1
    elif keys[pygame.K_a]:
        translate_vector_y = -1
    else:
        translate_vector_y = 0

    setpoint_heading = math.atan2(translate_vector_y, translate_vector_x)
    translate_power = min(math.sqrt(translate_vector_x**2 + translate_vector_y**2), 1)

    spin_angle += spin_speed
    spin_angle %= 2 * math.pi

    point_angles = [(i * (2 * math.pi / num_points) + spin_angle) % (2 * math.pi) for i in range(num_points)]
    pygame.draw.circle(screen, (100, 100, 255), center, radius, 2)

    offset_heading = (setpoint_heading + math.pi) % (2 * math.pi)

    sum_fx = 0
    sum_fy = 0
    sum_px = 0
    sum_py = 0
    total_force_mag = 0

    for angle in point_angles:
        draw_angle = angle - math.pi / 2
        x = center[0] + radius * math.cos(draw_angle)
        y = center[1] + radius * math.sin(draw_angle)

        diff = angle_diff(angle, offset_heading)
        mag = math.sin(diff)
        if mag < 0:
            mag = 0

        tangent_angle = angle + math.pi / 2
        tx = math.cos(tangent_angle - math.pi / 2)
        ty = math.sin(tangent_angle - math.pi / 2)

        force_scale = 100
        fx = mag * translate_power * tx * force_scale
        fy = mag * translate_power * ty * force_scale

        sum_fx += fx
        sum_fy += fy

        # For weighted average position
        sum_px += x * (abs(fx) + abs(fy))
        sum_py += y * (abs(fx) + abs(fy))
        total_force_mag += abs(fx) + abs(fy)

        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 6)
        pygame.draw.line(screen, (255, 100, 100), (x, y), (x + fx, y + fy), 3)

    if total_force_mag > 0:
        avg_px = sum_px / total_force_mag
        avg_py = sum_py / total_force_mag

        net_scale = 1.5
        net_fx = sum_fx * net_scale
        net_fy = sum_fy * net_scale

        pygame.draw.line(screen, (100, 255, 100), (avg_px, avg_py), (avg_px + net_fx, avg_py + net_fy), 5)
        pygame.draw.circle(screen, (100, 255, 100), (int(avg_px + net_fx), int(avg_py + net_fy)), 8)

        # Draw torque from center
        r_x = avg_px - center[0]
        r_y = avg_py - center[1]
        torque = r_x * sum_fy - r_y * sum_fx
        draw_torque_arc(screen, center, torque)

    sp_x = center[0] + radius * math.cos(setpoint_heading - math.pi / 2)
    sp_y = center[1] + radius * math.sin(setpoint_heading - math.pi / 2)
    pygame.draw.line(screen, (255, 255, 0), center, (sp_x, sp_y), 3)

    text = font.render(
        f'Setpoint Heading: {math.degrees(setpoint_heading):.1f}°  |  Spin Speed: {math.degrees(spin_speed):.1f}°/frame',
        True, (200, 200, 200)
    )
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
