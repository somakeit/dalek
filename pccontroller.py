import pygame
import socket
import sys, getopt

joystickid = 0
try:
  opts, args = getopt.getopt(sys.argv[1:], "hj:")
except getopt.GetoptError as err:
  print str(err)
  exit(1)
for opt, arg in opts:
  if opt == "-h":
    print "Davros Industries - PC Controller v0.1"
    print "pccontroller [-j <joystick_index] <server_ip/name> <port>"
    print "  -j ID of joystick to use, default = 0."
    print "  -h This."
    exit(2)
  elif opt == "-j":
    try:
      joystickid = int(arg)
    except ValueError:
      print "Joystick (-j) should be a number."
      exit(1)
servername = sys.argv[len(sys.argv) - 2]
try:
  serverport = int(sys.argv[len(sys.argv) - 1])
except ValueError:
  print "Port sould be a number"
  exit(1)

pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

print "Davros Industries - PC Controller"
print "================================="
print "Found", len(joysticks), "controllers:"
for joystick in joysticks:
  print "  ", joystick.get_name()

if len(joysticks) < joystickid + 1:
  print "Invalid joystick id:", joystickid
  exit(1)

joystick = joysticks[joystickid]
joystick.init()
if joystick.get_numaxes() < 2:
  print "Joystick has insufficient axes, need at leat 2 (where did you get that thing?)"
  exit(1)
if joystick.get_numbuttons() < 1:
  print "Joystick has insufficient buttons, need at least 1."
  exit(1)
print "Using:", (joystick.get_name())

print "Connecting to server", servername, "on port", serverport
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  server.connect((servername, serverport))
except socket.error as err:
  print str(err)
  exit(1)
print "Connected to server."

print "Move joystick in full circle, return to center then press button 0."
x = 0.0
y = 0.0

calibrated = False
xmin = 1.0; #xmin is expected to be negative, but a really bad stick might not go below 0.
xori = 0.0;
xmax = -1.0;
ymin = 1.0;
yori = 0.0;
ymax = -1.0;

while True:
  for event in pygame.event.get():
     if event.type == pygame.JOYAXISMOTION:
       #if it's exactly 0.0, take the last reading
       xn = joystick.get_axis(0)
       yn = joystick.get_axis(1)
       if xn != 0.0: x = xn
       if yn != 0.0: y = yn

       
       if calibrated:
         xval = 0.0
         yval = 0.0
         if x < xori:
           xval = 0 - (x - xori) / (xmin - xori)
           if xval < -1.0: xval = -1.0
         else:
           xval = (x - xori) / (xmax - xori)
           if xval > 1.0: xval = 1.0
         if y < yori:
           yval = 0 - (y - yori) / (ymin - yori)
           if yval < -1.0: yval = -1.0
         else:
           yval = (y - yori) / (ymax - yori)
           if yval > 1.0: yval = 1.0
         server.send("X" + str(xval) + "Y" + str(yval) + "\n")
       else:
         if x > xmax: xmax = x
         if x < xmin: xmin = x
         if y > ymax: ymax = y
         if y < ymin: ymin = y
       

     if event.type == pygame.JOYBUTTONDOWN:
       if not calibrated:
         xori = x
         yori = y
         if (xmin - xori == 0) or (xmax - xori == 0) or (ymin - yori == 0) or (ymax - yori == 0):
           #this also prevents division by 0
           print "Range is nill, calibrate again..."
         else:
           calibrated = True
           print "Calibration complete, control will be enabled."

