#!/bin/bash

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
 
#pulseaudio -D

#SOURCE=alsa_input.usb-0d8c_C-Media_USB_Headphone_Set-00-Set.analog-mono
#SINK=alsa_output.usb-0d8c_C-Media_USB_Headphone_Set-00-Set.analog-stereo

#AUDIONAME=usb-0d8c_USB_PnP_Sound_Device-00-Device
AUDIONAME=usb-0d8c_C-Media_USB_Headphone_Set-00-Set
SOURCE=alsa_input.$AUDIONAME.analog-mono
SINK=alsa_output.$AUDIONAME.analog-stereo

pactl suspend-source $SOURCE 0
pactl suspend-sink $SINK 0
pacmd set-default-source $SOURCE
pacmd set-default-sink $SINK

echo "Booting..." | festival --tts

PULSE_SOURCE=$SOURCE PULSE_SINK=$SINK /usr/bin/aplay -D pulse silent.wav

MOD1=$(pactl load-module module-ladspa-sink sink_name=filter master=$SINK channels=1 rate=22050 plugin=ringmod_1188 label=ringmod_1i1o1l control=2,30,1,0,0,0)
MOD2=$(pactl load-module module-ladspa-sink sink_name=dalek master=filter channels=1 rate=22050 plugin=single_para_1203 label=singlePara control=8,200,1)
#MOD1=$(pactl load-module module-ladspa-sink sink_name=dalek master=$SINK channels=1 rate=22050 plugin=ringmod_1188 label=ringmod_1i1o1l control=2,30,1,0,0,0)

PULSE_SOURCE=$SOURCE PULSE_SINK=$SINK /usr/bin/aplay -D pulse silent.wav
export PULSE_SINK=dalek
echo "Audio system is online!" | festival --tts
/usr/bin/alsaloop -c 1 --rate=44100 -A 3 -b -S 5 -C pulse -P pulse -t 50000
#/usr/bin/alsaloop -c 1 --rate=48000 -A 3 -b -S 5 -C pulse -P pulse -t 50000
#/usr/bin/alsaloop -c 1 --rate=44100 -C pulse -P pulse -t 50000

pactl unload-module $MOD2
pactl unload-module $MOD1
echo "Audio system shut down" | festival --tts

#pulseaudio --kill
