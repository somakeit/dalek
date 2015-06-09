#!/usr/bin/python

"""
Send 8-bit PulseAudio peak sound samples to a digital-to-analog convertor
(which is intended to be connected to an analog VU meter).

Because it requires access to the GPIO pins, this program is intended to be run
as root. After the pins are initialised, it will change uid to AUDIO_USER in
order to sample peak audio levels from PulseAudio. Set AUDIO_USER as
appropriate.
"""

import os
import pwd

import dac
from peak_monitor import PeakMonitor


AUDIO_USER = 'mpd'  # The user running the PulseAudio daemon that's writing to
                    # the audio outputs
SINK_NAME = 'alsa_output.platform-bcm2835_AUD0.0.analog-stereo'
METER_RATE = 128    # Hz

def change_uid(username):
    account = pwd.getpwnam(username)
    os.setuid(account.pw_uid)
    os.environ['HOME'] = account.pw_dir

def main():
    dac.init()   # Set up the GPIO pins used to talk to the DAC

    change_uid(AUDIO_USER)

    for sample in PeakMonitor(SINK_NAME, METER_RATE):
        # samples range from 0 to 127 so double them to get the full voltage
        # range of the DAC
        dac.write_byte(sample << 1)

if __name__ == '__main__':
    main()
