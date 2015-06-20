#!/usr/bin/python

import pwm
from peak_monitor import PeakMonitor

SINK_NAME = 'alsa_output.usb-0d8c_C-Media_USB_Headphone_Set-00-Set.analog-stereo'
METER_RATE = 128    # Hz
SMOOTHING = 4.0
FILTER_LENGTH = 10
FILTER_GOOD = 7


val = 0

def main():
    global val
    samples = []
    pwm.init()

    for sample in PeakMonitor(SINK_NAME, METER_RATE):
        # samples range from 0 to 127
        scaled_sample = (sample - 40)/50.0
        scaled_sample = min(1.0, max(0.0, scaled_sample))

        # Filter out crackles and other spikes
        samples.append(scaled_sample)
        samples = samples[-FILTER_LENGTH:]
        calc = samples[:]
        calc.sort()
        scaled_sample = sum(calc[0:FILTER_GOOD]) / (1.0 * FILTER_GOOD)

        val = val * ((SMOOTHING-1)/SMOOTHING) + scaled_sample * (1/SMOOTHING)
        pwm.write(val)

if __name__ == '__main__':
    main()
