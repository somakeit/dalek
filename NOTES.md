Notes
=====

Alsa volume level comes out of sync
-----------------------------------

To solve, adjust it correctly, then `alsactl store 1 -f ~/asound.state`
then add a cron job (every minute, why not) to `alsactl restore 1 -f
~/asound.state`

There's a delay on the audio
----------------------------

Give it a couple minutes, it seems to take a while to settle down.

