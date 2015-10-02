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

    left = y_ratio + x_ratio
    right = y_ratio - x_ratio

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


