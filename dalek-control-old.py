import pygame
import time
from math import log, floor, atan, sqrt, cos, exp, atan2, pi, sin

pygame.init()
pygame.joystick.init()

js = pygame.joystick.Joystick(0);
js.init()

name = js.get_name()
print "Joystick: " + str(name)

size = [600, 300]
screen = pygame.display.set_mode(size)

def xy2motors(pair):
    x, y = pair
    center_tolerance = 5
    x_center = 128.0
    x_min = 40.0
    y_center = 128.0
    y_min = 40.0

    # Prevent jitter on centred nunchucks
    if abs(x - x_center) < center_tolerance:
        x = x_center
    if abs(y - y_center) < center_tolerance:
        y = y_center

    x_ratio = (x - x_center) / (x_center - x_min)
    y_ratio = (y - y_center) / (y_center - y_min)
    # clamp to -1..1
    x_ratio = min(1.0, max(-1.0, x_ratio))
    y_ratio = min(1.0, max(-1.0, y_ratio))

    if x_ratio == y_ratio == 0:
        left = 0
        right = 0
    else:
        r = sqrt(x_ratio ** 2 + y_ratio ** 2)
        angle = atan2(y_ratio, x_ratio)
        # Take angle about y axis instead of x.
        angle = pi/2.0 - angle

        speed = r
        if speed >= 1:
            speed = 1

        if angle < -pi/2.0:
            left = -speed
        elif angle < -pi/4.0:
            pos = (angle - (-pi/2.0)) / (pi / 4.0)
            start = - speed
            stop = speed / 2
            left = start + (stop - start) * pos
        elif angle <= 0:
            left = cos(angle) * speed
        elif angle < pi/2.0:
            left = speed
        elif angle < 3*pi/4.0:
            left = cos(angle - pi/2.0) * speed
        else:
            pos = (angle - 3*pi/4.0) / (pi / 4.0)
            start = speed / 2
            stop = - speed
            left = start + (stop - start) * pos

        if angle > pi/2.0:
            right = -speed
        elif angle > pi/4.0:
            pos = (angle - (pi/4.0)) / (pi / 4.0)
            start = speed / 2
            stop = - speed
            right = start + (stop - start) * pos
        elif angle >= 0:
            right = cos(angle) * speed
        elif angle > -pi/2.0:
            right = speed
        elif angle > -3*pi/4.0:
            right = cos(angle + pi/2.0) * speed
        else:
            pos = (angle + pi) / (pi / 4.0)
            start = - speed
            stop = speed / 2
            right = start + (stop - start) * pos

    # clamp to -1..1
    left = min(1.0, max(-1.0, left)) * 0.9999999
    right = min(1.0, max(-1.0, right)) * 0.9999999

    return left, right

while True:
    pygame.event.pump()

    x = (js.get_axis(0) + 1) * 128;
    y = (-js.get_axis(1) + 1) * 128;
    
    print str(x) + " " + str(y)

    left, right = xy2motors((x, y))

    print str(left) + " " + str(right)

    screen.fill((0,0,0))
    pygame.draw.line(screen, (255,0,0), [100, 150], [100,int(150 - left * 50)], 5)
    pygame.draw.line(screen, (0,255,0), [200, 150], [200,int(150 - right * 50)], 5)
    pygame.draw.circle(screen, (0,0,255), [int(322 + x), int(278 - y)], 5)
    pygame.display.flip()


