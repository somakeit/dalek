from __future__ import division # I always want float division
import cwiid, time, StringIO, sys, socket, os
from math import log, floor, atan, sqrt, cos, exp, atan2, pi, sin
import serial

os.chdir(os.path.dirname(os.path.realpath(__file__)))

SPEED_MAX = 15
SPEED_MIN = 1

def do_scale(input, max, divisor=None):
    if divisor is None: divisor = max
    if (input > 1): input = 1
    if (input < -1): input = -1
    input = int(input * divisor)
    if input > max: input = max
    elif input < -max: input = -max
    return input

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

class Dalek:
    ser = None
    last_sent = None
    speed_multiplier = floor(SPEED_MIN + (SPEED_MAX - SPEED_MIN)/2)
    last_play = time.time()

    def __init__(self, wiimote):
        self.wiimote = wiimote
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        self.wiimote.led(self.speed_multiplier)

    def online(self):
        print("Dalek online :)")
        self.wiimote.led(self.speed_multiplier)

    def offline(self):
        print("Dalek offline :(")
        self.stop()

    def stop(self):
        self.send("M00000\n")

    def motor(self, pair):
        left, right = pair
        left *= self.speed_multiplier / SPEED_MAX
        right *= self.speed_multiplier / SPEED_MAX
        letters = "0123456789abcdef"
        if left < 0 and right < 0:
            direction = '3'
        elif right < 0:
            direction = '2'
        elif left < 0:
            direction = '1'
        else:
            direction = '0'
        left = int(floor(abs(left * 256)))
        right = int(floor(abs(right * 256)))
        string_to_send = "M"
        #string_to_send += "+"
        string_to_send += letters[left >> 4]
        string_to_send += letters[left & 15]
        #string_to_send += "+"
        string_to_send += letters[right >> 4]
        string_to_send += letters[right & 15]
        string_to_send += direction
        string_to_send += "\n"
        self.send(string_to_send)

    def send(self, string_to_send):
        if string_to_send <> self.last_sent:
            self.last_sent = string_to_send
            self.ser.write(string_to_send)
            w = self.ser.inWaiting()
            if w > 0:
                print self.ser.read(w)
            print string_to_send

    def play(self, filename):
        print("Play " + filename)
        if time.time() - self.last_play < 2:
            return
        self.last_play = time.time()
        os.system("/usr/bin/mpg123 sounds/" + filename + " &")

    def increase_speed(self):
        self.speed_multiplier += 1
        if self.speed_multiplier > SPEED_MAX:
            self.speed_multiplier = SPEED_MAX
        self.wiimote.led(self.speed_multiplier)

    def decrease_speed(self):
        self.speed_multiplier -= 1
        if self.speed_multiplier < SPEED_MIN:
            self.speed_multiplier = SPEED_MIN
        self.wiimote.led(self.speed_multiplier)

class Wiimote:
    wm = None
    dalek = None
    wii_calibration = None
    #Initialize variables
    #reportvals = {"accel":cwiid.RPT_ACC, "button":cwiid.RPT_BTN, "ext":cwiid.RPT_EXT,  "status":cwiid.RPT_STATUS}
    reportvals = {"accel":cwiid.RPT_ACC, "button":cwiid.RPT_BTN, "ext":cwiid.RPT_EXT,  "status":cwiid.RPT_STATUS}
    report={"accel":False, "button":True, "ext": True}
    state = {"acc":[0, 0, 1], "nunchuck_stick": (130, 130)}
    lasttime = 0.0
    laststate = {}
    lastaction = 0.0
    responsiveness = 0.15
    firstPress = True
    firstPressDelay = 0.5
    maxButtons = 0

    def __init__(self):
        self.dalek = Dalek(self)

    def rumble(self,delay=0.2): # rumble unit - default = 0.2 seconds
        self.wm.rumble=1
        time.sleep(delay)
        self.wm.rumble=0

    def led(self, nr):
        if not self.wm:
            return
        self.wm.led = nr #cwiid.LED1_ON | cwiid.LED4_ON

    def wmconnect(self):
        try:
            self.wm = cwiid.Wiimote()
        except:
            self.wm = None
            self.dalek.offline()
            return None
        print "Connected to a wiimote :)"
        self.lastaction = time.time()
        self.rumble()
        # Wiimote calibration data (cache this)
        self.wii_calibration = self.wm.get_acc_cal(cwiid.EXT_NONE)
        self.dalek.online()
        return self.wm

    def wmcb(self, messages, extra=None):
        state = self.state
        for message in messages:
            if message[0] == cwiid.MESG_BTN:
                state["buttons"] = message[1]
            #elif message[0] == cwiid.MESG_STATUS:
            #   print "\nStatus: ", message[1]
            elif message[0] == cwiid.MESG_ERROR:
                if message[1] == cwiid.ERROR_DISCONNECT:
                    self.wm = None
                    self.dalek.offline()
                    continue
                else:
                    self.wm.close()
                    self.wm = None
                    self.dalek.offline()
                    print "ERROR: ", message[1]
            elif message[0] == cwiid.MESG_ACC:
                state["acc"] = message[1]
            elif message[0] == cwiid.MESG_NUNCHUK:
                state["nunchuck_acc"] = message[1]['acc']
                state["nunchuck_buttons"] = message[1]['buttons']
                state["nunchuck_stick"] = message[1]['stick']
            else:
                print "Unknown message!", message
                continue
            self.dalek.motor(xy2motors(state["nunchuck_stick"]))
            laststate = self.laststate
            if ('buttons' in laststate) and (laststate['buttons'] <> state['buttons']):
                # Buttons changed
                if state['buttons'] == 0:
                    self.maxButtons = 0
                elif state['buttons'] < self.maxButtons:
                    continue # You released a button!
                else:
                    self.maxButtons = state['buttons']
                self.lasttime = 0
                self.firstPress = True
                if laststate['buttons'] == cwiid.BTN_B and not state['buttons'] == cwiid.BTN_B:
                    # We were holding B, but no longer!
                    state.pop('BTN_B', None)
                if (laststate['buttons'] & cwiid.BTN_A and laststate['buttons'] & cwiid.BTN_B) and not (state['buttons'] & cwiid.BTN_A and state['buttons'] & cwiid.BTN_B):
                    # We were holding both A and B, but no longer!
                    state.pop('BTN_AB', None)
            if (state["buttons"] > 0) and (time.time() > self.lasttime + self.responsiveness):
                # Time to process these buttons!
                self.lasttime = time.time()
                wasFirstPress = False
                if self.firstPress:
                    wasFirstPress = True
                    self.lasttime = self.lasttime + self.firstPressDelay
                    self.firstPress = False

                # ----------------------------------------------
                # Stuff that doesn't need roll/etc calculations

                # Sound effects
                if state["buttons"] == cwiid.BTN_HOME:
                    self.dalek.play("btn_home.mp3")
                if state["buttons"] == cwiid.BTN_A:
                    self.dalek.play("btn_a.mp3")
                if state["buttons"] == cwiid.BTN_B:
                    self.dalek.play("btn_b.mp3")
                if state["buttons"] == cwiid.BTN_UP:
                    self.dalek.play("btn_up.mp3")
                if state["buttons"] == cwiid.BTN_DOWN:
                    self.dalek.play("btn_down.mp3")
                if state["buttons"] == cwiid.BTN_LEFT:
                    self.dalek.play("btn_left.mp3")
                if state["buttons"] == cwiid.BTN_RIGHT:
                    self.dalek.play("btn_right.mp3")
                if state["buttons"] == cwiid.BTN_1:
                    self.dalek.play("btn_1.mp3")
                if state["buttons"] == cwiid.BTN_2:
                    self.dalek.play("btn_2.mp3")

                # Speeds
                if state["buttons"] == cwiid.BTN_MINUS:
                    self.dalek.decrease_speed()
                if state["buttons"] == cwiid.BTN_PLUS:
                    self.dalek.increase_speed()

                # ----------------------------------------------
                # Do we need to calculate roll, etc?
                # Currently only BTN_B needs this.
                """ # Python doesn't have block comments, so hack it with this.
                calcAcc = state["buttons"] & cwiid.BTN_B
                if calcAcc:
                    # Calculate the roll/etc.
                    X = self.wii_rel(state["acc"][cwiid.X], cwiid.X)
                    Y = self.wii_rel(state["acc"][cwiid.Y], cwiid.Y)
                    Z = self.wii_rel(state["acc"][cwiid.Z], cwiid.Z)
                    if (Z==0): Z=0.00000001 # Hackishly prevents divide by zeros
                    roll = atan(X/Z)
                    if (Z <= 0.0):
                        if (X>0): roll += 3.14159
                        else: roll -= 3.14159
                    pitch = atan(Y/Z*cos(roll))
                    #print "X: %f, Y: %f, Z: %f; R: %f, P: %f; B: %d    \r" % (X, Y, Z, roll, pitch, state["buttons"]),
                    sys.stdout.flush()
                if state["buttons"] & cwiid.BTN_B and state["buttons"] & cwiid.BTN_LEFT:
                    self.dalek.cmd('play seek beginning')
                if state["buttons"] & cwiid.BTN_B and state["buttons"] & cwiid.BTN_A:
                    speed=do_scale(roll/3.14159, 20, 25)
                    if (speed<-10): speed = -10
                    state['BTN_AB'] = speed
                    cmd = ""
                    # on first press,  press a,
                    # after then use the diff to press left/right
                    if not 'BTN_AB' in laststate:
                        # # query location
                        # Playback Recorded 00:04:20 of 00:25:31 1x 30210 2008-09-10T09:18:00 6523 /video/30210_20080910091800.mpg 25
                        cmd += "play speed normal\nkey a\n"#"play speed normal\n"
                    else:
                        speed = speed - laststate['BTN_AB']
                    if speed > 0:
                        cmd += (speed / 5) * "key up\n" # Floor is automatic
                        cmd += (speed % 5) * "key right\n"
                    elif speed < 0:
                        cmd += (-speed / 5) * "key down\n" # Floor is automatic
                        cmd += (-speed % 5) * "key left\n"
                    if speed <> 0:
                        self.rumble(.05)
                    if cmd is not None and cmd:
                        self.dalek.raw(cmd)
                if state["buttons"] == cwiid.BTN_B:
                    speed=do_scale(roll/3.14159, 8, 13)
                    state['BTN_B'] = speed
                    if not 'BTN_B' in laststate:
                        # # query location
                        # Playback Recorded 00:04:20 of 00:25:31 1x 30210 2008-09-10T09:18:00 6523 /video/30210_20080910091800.mpg 25
                        cmd = ""#"play speed normal\n"
                        if speed > 0:
                            cmd += "key .\n"
                        elif speed < 0:
                            cmd += "key ,\n"
                        if speed <> 0:
                            cmd += "key "+str(abs(speed)-1)+"\n"
                        #print cmd
                    elif laststate['BTN_B']<>speed:
                        self.rumble(.05)
                        if speed == 0:
                            cmd = "play speed normal"
                        elif ((laststate['BTN_B'] > 0) and (speed > 0)) or ((laststate['BTN_B'] < 0) and (speed < 0)):
                            cmd = "key "+str(abs(speed)-1)+"\n"
                        elif speed>0:
                            cmd = "key .\nkey "+str(abs(speed)-1)+"\n"
                        else:
                            cmd = "key ,\nkey "+str(abs(speed)-1)+"\n"
                    else:
                        cmd = None
                    if cmd is not None:
                        self.dalek.raw(cmd)
                """
            self.laststate = state.copy() #NOTE TO SELF: REMEMBER .copy() !!!

    def main(self):
        print "Scanning for wii remotes."
        while True:
            if self.wm is None:
                #Connect wiimote
                self.wmconnect()
                if self.wm:
                    #Tell Wiimote to display rock sign
                    self.wm.led = cwiid.LED1_ON | cwiid.LED4_ON
                    self.wm.rpt_mode = sum(self.reportvals[a] for a in self.report if self.report[a])
                    self.wm.enable(cwiid.FLAG_MESG_IFC | cwiid.FLAG_REPEAT_BTN)
                    self.wm.mesg_callback = self.wmcb
                    self.lastaction = time.time()
                else:
                    print "Retrying... "
                    print
            time.sleep(0.05)
        print "Exited Safely"

# Instantiate our class, and start.
inst = Wiimote()
inst.main()
