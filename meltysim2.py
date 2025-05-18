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
num_points = 4

# global variables
spin_angle = 0.0 # simulation global angle of the robot
spin_speed = 0.1*math.pi  # radians per frame for simulation
spin_speed_step = math.radians(0.5)  # how much spin_speed changes per key cycle
translate_vector_x = 0.0
translate_vector_y = 0.0 # vector used to express desired movement in cartesian coordinate frame
translate_power = 0.0 # translation power
setpoint_heading = 0.0 # direction setpoint

# find difference in two angles and wrap to [-pi, pi] interval
def angle_diff(a, b):
    diff = a - b
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

# main loop
running = True
while running:
    screen.fill((30, 30, 30))

    #handle instance end gracefully
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #get keys that are pressed
    keys = pygame.key.get_pressed()

    #compose Y vector component
    if keys[pygame.K_w]:
        translate_vector_x = 1
    elif keys[pygame.K_s]:
        translate_vector_x = -1
    else:
        translate_vector_x = 0
    
    #compose X vector component
    if keys[pygame.K_d]:
        translate_vector_y = 1
    elif keys[pygame.K_a]:
        translate_vector_y = -1
    else:
        translate_vector_y = 0
    
    #extrapolate vector direction from X and Y components
    setpoint_heading = math.atan2(translate_vector_y, translate_vector_x)

    #extrapolate magnitude from X and Y components, and clamp to 1
    translate_power = min(math.sqrt(translate_vector_x**2 + translate_vector_y**2), 1)


    #update spin speed
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
        # Shift angle so zero is up
        x = center[0] + radius * math.cos(angle - math.pi / 2)
        y = center[1] + radius * math.sin(angle - math.pi / 2)

        diff = angle_diff(angle, offset_heading)

        mag = math.sin(diff)
        if mag < 0:
            mag = 0  # one direction only

        tangent_angle = angle + math.pi / 2
        tx = math.cos(tangent_angle - math.pi / 2)
        ty = math.sin(tangent_angle - math.pi / 2)

        force_scale = 100

        fx = mag * translate_power * tx * force_scale 
        fy = mag * translate_power * ty * force_scale

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

    # Setpoint heading line rotated so zero is up
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
