#!/usr/bin/env python2
#

import mpd

## Define MPD Connection
client = mpd.MPDClient()
# Reconnect
while 1:
    try:
        status = client.status()
        print("Initial connect")
        #os.system("amixer -q sset PCM 80%") 
        #os.system("mpg123 startup.mp3")
        print("Done!")
        break

    except:
            client.connect("localhost", 6600)
            print("Initial connect failed ...")


playing = client.status()

print playing["state"]
