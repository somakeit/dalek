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

root can't access pulseaudio running as user
--------------------------------------------

Follow these instructions:

http://billauer.co.il/blog/2014/01/pa-multiple-users/

As pi:

```sh
cp /etc/pulse/default.pa ~/.pulse/
echo "load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1" >> ~/.pulse/default.pa
```

As root:

```sh
echo "default-server = 127.0.0.1" > ~/.pulse/client.conf
```
