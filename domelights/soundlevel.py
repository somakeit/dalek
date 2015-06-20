#!/usr/bin/python

import pwm
from peak_monitor import PeakMonitor

SINK_NAME = 'alsa_output.usb-0d8c_C-Media_USB_Headphone_Set-00-Set.analog-stereo'
METER_RATE = 128    # Hz
SMOOTHING = 2.0


val = 0

def main():
    global val
    samples = []
    pwm.init()

    for sample in PeakMonitor(SINK_NAME, METER_RATE):
        # samples range from 0 to 127
        scaled_sample = (sample - 40)/50.0
        scaled_sample = min(1, max(0, scaled_sample))

        # Filter out crackles and other spikes
        samples.append(scaled_sample)
        samples = samples[-5:]
        calc = samples[:]
        calc.sort()
        val = sum(calc[0:3])/3.0

        #val = val * ((SMOOTHING-1)/SMOOTHING) + scaled_sample * (1/SMOOTHING)
        pwm.write(val)

if __name__ == '__main__':
    main()
