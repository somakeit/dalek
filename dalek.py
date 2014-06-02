import cwiid, time, StringIO, sys, socket, os
from math import log, floor, atan, sqrt, cos, exp, atan2, pi, sin
import serial

max_speed = 0.3

def do_scale(input, max, divisor=None):
	if divisor is None: divisor = max
	if (input > 1): input = 1
	if (input < -1): input = -1
	input = int(input * divisor)
	if input>max: input = max
	elif input < -max: input = -max
	return input

def xy2motors(pair):
	x, y = pair
	x_center = 130.0
	x_min = 35.0
	x_ratio = (x - x_center) / (x_center - x_min)
	y_center = 129.0
	y_min = 34.0
	y_ratio = (y - y_center) / (y_center - y_min)
	if abs(x_ratio) < 0.1:
		x_ratio = 0.0
	if abs(y_ratio) < 0.1:
		y_ratio = 0.0

	r = sqrt(x_ratio ** 2 + y_ratio ** 2)
	angle = atan2(y_ratio, x_ratio)
	speed = r
	if speed >= 1:
		speed = 0.99999
	if angle < 0.0:
		speed = -speed
	direction = abs(angle) - pi/2.0
	#print x_ratio, y_ratio, r, angle, speed, direction
	left = speed
	right = speed
	factor = cos(direction)
	if direction > 0.0:
		left *= factor
	else:
		right *= factor
	left *= max_speed
	right *= max_speed
	return left, right

class Dalek:
	ser = None
	last_sent = None

	def __init__(self, owner):
		self.owner = owner
		self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

	def stop(self):
		self.send(";Maaaaa")

	def motor(self, pair):
		left, right = pair
		letters = "abcdefghijklmnop"
		if left < 0 and right < 0:
			direction = 'd'
		elif right < 0:
			direction = 'c'
		elif left < 0:
			direction = 'b'
		else:
			direction = 'a'
		left = int(floor(abs(left * 256)))
		right = int(floor(abs(right * 256)))
		string_to_send = ";M"
		string_to_send += letters[left >> 4]
		string_to_send += letters[left & 15]
		string_to_send += letters[right >> 4]
		string_to_send += letters[right & 15]
		string_to_send += direction
		self.send(string_to_send)

	def send(self, string_to_send):
		if string_to_send <> self.last_sent:
			self.last_sent = string_to_send
			self.ser.write(string_to_send)
			print string_to_send

class Wiimote:
	wm = None
	dalek = None
	wii_calibration = None
	#Initialize variables
	reportvals = {"accel":cwiid.RPT_ACC, "button":cwiid.RPT_BTN, "ext":cwiid.RPT_EXT,  "status":cwiid.RPT_STATUS}
	report={"accel":False, "button":True, "ext": True}
	state = {"acc":[0, 0, 1], "nunchuck_stick": (0, 0)}
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

	def wmconnect(self):
		try:
			self.wm = cwiid.Wiimote()
		except:
			self.wm = None
			self.dalek.stop()
			return None
		print "Connected to a wiimote :)"
		self.lastaction = time.time()
		self.rumble()
		# Wiimote calibration data (cache this)
		self.wii_calibration = self.wm.get_acc_cal(cwiid.EXT_NONE)
		return self.wm

	def wmcb(self, messages, extra=None):
		state = self.state
		for message in messages:
			if message[0] == cwiid.MESG_BTN:
				state["buttons"] = message[1]
			#elif message[0] == cwiid.MESG_STATUS:
			#	print "\nStatus: ", message[1]
			elif message[0] == cwiid.MESG_ERROR:
				if message[1] == cwiid.ERROR_DISCONNECT:
					self.wm = None
					self.dalek.stop()
					continue
				else:
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
			continue
			# Stuff from MythPyWii
			laststate = self.laststate
			if ('buttons' in laststate) and (laststate['buttons'] <> state['buttons']):
				if state['buttons'] == 0:
					self.maxButtons = 0
				elif state['buttons'] < self.maxButtons:
					continue
				else:
					self.maxButtons = state['buttons']
				self.lasttime = 0
				self.firstPress = True
				if laststate['buttons'] == cwiid.BTN_B and not state['buttons'] == cwiid.BTN_B:
					del state['BTN_B']
					if not (state['buttons'] & cwiid.BTN_B):
						self.ms.cmd('play speed normal')
				if (laststate['buttons'] & cwiid.BTN_A and laststate['buttons'] & cwiid.BTN_B) and not (state['buttons'] & cwiid.BTN_A and state['buttons'] & cwiid.BTN_B):
					del state['BTN_AB']
					#self.ms.cmd('play speed normal')
			if self.ms.ok() and (self.wm is not None) and (state["buttons"] > 0) and (time.time() > self.lasttime+self.responsiveness):
				self.lasttime = time.time()
				wasFirstPress = False
				if self.firstPress:
					wasFirstPress = True
					self.lasttime = self.lasttime + self.firstPressDelay
					self.firstPress = False
				# Stuff that doesn't need roll/etc calculations
				if state["buttons"] == cwiid.BTN_HOME:
					self.ms.cmd('key escape')
				if state["buttons"] == cwiid.BTN_A:
					self.ms.cmd('key enter')
				if state["buttons"] == cwiid.BTN_MINUS:
					self.ms.cmd('key d')
				if state["buttons"] == cwiid.BTN_UP:
					self.ms.cmd('key up')
				if state["buttons"] == cwiid.BTN_DOWN:
					self.ms.cmd('key down')
				if state["buttons"] == cwiid.BTN_LEFT:
					self.ms.cmd('key left')
				if state["buttons"] == cwiid.BTN_RIGHT:
					self.ms.cmd('key right')
				if state["buttons"] == cwiid.BTN_PLUS:
					self.ms.cmd('key p')
				if state["buttons"] == cwiid.BTN_1:
					self.ms.cmd('key i')
				if state["buttons"] == cwiid.BTN_2:
					self.ms.cmd('key m')
				# Do we need to calculate roll, etc?
				# Currently only BTN_B needs this.
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
					#print "X: %f, Y: %f, Z: %f; R: %f, P: %f; B: %d	\r" % (X, Y, Z, roll, pitch, state["buttons"]),
					sys.stdout.flush()
				if state["buttons"] & cwiid.BTN_B and state["buttons"] & cwiid.BTN_LEFT:
					self.ms.cmd('play seek beginning')
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
						self.ms.raw(cmd)
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
						self.ms.raw(cmd)
			self.laststate = state.copy() #NOTE TO SELF: REMEMBER .copy() !!!

	def main(self):
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
