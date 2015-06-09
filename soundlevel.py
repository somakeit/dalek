#!/usr/bin/python

import pwm
from peak_monitor import PeakMonitor

SINK_NAME = 'alsa_output.platform-bcm2835_AUD0.0.analog-stereo'
METER_RATE = 128    # Hz

def main():
    pwm.init()

    for sample in PeakMonitor(SINK_NAME, METER_RATE):
        # samples range from 0 to 127
        pwm.write(sample/127)

if __name__ == '__main__':
    main()
