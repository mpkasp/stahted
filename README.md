Stahted
=====

A way to notify friends in the physical world by messaging them in Slack. Works well if you purchase this 
[Fun Express - Flashing Mini Red Beacon Light. (4 1/4" )](https://www.amazon.com/Fun-Express-Flashing-Beacon-Light/dp/B01449OW9W/ref=pd_day0_hl_328_2/131-0166910-1539612), open it up and hook it up to a FET or Relay driven by an RPi GPIO.

Setup
-----
1. `cp ./keys.example.py ./keys.py` and create a bot, and grab your key [here](https://my.slack.com/services/new/bot).

2. Pull the files on this repo to your rpi and add them to your /etc/rc.local so the start at boot

3. `pip3 install requirements.txt`

4. You may need to make sure bluetooth starts in advertising mode, check out `bluetoothctl` and you can probably just create a bash script to get it to work.


Notes
----
Learnings were taking from (blog.benjie.me)[https://blog.benjie.me/building-a-slack-bot-to-talk-with-a-raspberry-pi/], and (this project to setup wifi via an android phone over bluetooth)[https://github.com/brendan-myers/rpi3-wifi-conf-android]. I don't have as great of a readme but you can probably figure it out with my code and their links :)

TODO: make rpi3-wifi-conf.py work nicer with stahted.py, e.g. both using python3 would be a great start :)