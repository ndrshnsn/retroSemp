#!/usr/bin/env python2
#
#######################
## OPERATION
#######################
# TREBLE (Analog Signal, Pot)
# Original signal is from 0-1023, but mapped from 0-9 and sent from Arduino,
#   adjusting alsaequal values accordingly with equalizer array
#
# VOLUME (Analog Signal, Pot)
# Original signal is from 0-1023, but mapped from 0-31 and sent from Arduino,
#   adjusting alsa master volume level percent
#
# STATION (Digital Signal, Mouse)
# Signal is sent incremented by mouse roller movement
#
# SELECTOR (Digital Signal, Selector)
# Signal is sent from Arduino with 0 (ON) and 1 (OFF), modifying radio with the combinations
# 0001 - Position 1 = Radio Streams (ROCK'n ROLL)
# 0011 - Position 2 = Radio Streams (OTHER)
# 0111 - Position 3 = Radio Streams (OLD RADIO)
# 1111 - Position 4 = Playlist from Media Center
#
#######################
## CONFIG's
####################### 
# EQUALIZER
# Install equal (PACAUR) alsa plugin for treble and bass control ( alsamixer -D equal )
# Add this content to .asoundrc
# ctl.equal {
#   type equal;
# }
# pcm.plugequal {
#   type equal;
#   slave.pcm "plug:dmix"
# }
# pcm.!default {
#   type plug;
#   slave.pcm plugequal;
# }
# audio_output {
#     type        "alsa"
#     name        "My ALSA EQ"
#     device        "plug:plugequal"
#     format        "44100:16:2"    # optional
#     mixer_device    "default"    # optional
#     mixer_control    "PCM"        # optional
#     mixer_index    "0"        # optional
# }
#
# MPD
# Adjust Config of /etc/mpd.conf
# Change user and group to root
# Add music directory ( music_directory /var/lib/mpd/music )
#    or create a symbolic link
# Owner of mpd lib ( chown mpd:mpd /var/lib/mpd/ -R )
# 

## Import Libs
#
import smbus
import time
import ConfigParser
import os
import functions
import mpd
from functions import *
from array import *

## Read Config File
#
config = ConfigParser.ConfigParser()
config.readfp(open(r'config.txt'))

## Define MPD Connection
client = mpd.MPDClient()
client.timeout = config.get('MPD', 'cTimeout')
client.idletimeout = config.get('MPD', 'cIdleTimeout')

# Reconnect
while 1:
    try:
        status = client.status()
        print("Initial connect")
        print("Done!")
        break

    except:
        client.connect(str(config.get('GENERAL', 'mpdHost')), int(config.get('GENERAL', 'mpdPort')))
        print("Initial connect failed ...")
        time.sleep(1)

## Load Playlists from Files
loadPlaylists("st", "./playlists/st.txt")
loadPlaylists("0", "./playlists/s0.txt")

## MPD Vars
list_len=len(client.playlist())
status = client.currentsong()
#songid=int(status['pos'])

## Station Control Vars
betweenStations = int(config.get('GENERAL', 'fadeWidth')) + int(config.get('GENERAL', 'staticWidth')) + int(config.get('GENERAL', 'fadeWidth'))
prevStation = None
last_tone = 0
last_dial = 0
last_volume = 0

## Tries to Open Station Control File and save into var
try:
    f = open('dial.tmp','r')
    try:
        last_dial = int(f.read())
    finally:
        f.close()
except IOError:
    pass

while True:
    if config.get('GENERAL', 'runMode') == "TEST":
        tone = input('Tone: ')
        volume = input('Volume: ')
        dial = input('Dial: ')
        selector = input('Selector: ')
    elif config.get('GENERAL', 'runMode') == "I2C":
        try:
            data = smbus.SMBus(int(config.get('GENERAL', 'busI2C'))).read_i2c_block_data(int(config.get('GENERAL', 'busAddress')), 0);

            tone = data[0]
            volume = data[1]
            dial = data[2]
            selector = data[3]

        except:
            print "Error getting data from I2C Bus\n"

    ## If station read is bigger or lower than 1, turn it into positive 1 or negative 1
    dialPosition = last_dial
    if last_dial >= 0:
    	if dial >= 1 and dial <= 50:
    		dialPosition = last_dial + 1
    	elif last_dial != 0 and dial >= 200:
    		dialPosition = last_dial - 1

    ## Define Tone
    if tone != last_tone:
        last_tone = tone
        setEqual(tone)

    ## Define Volume
    if volume != last_volume:
		volFactor = volMap(volume, 0, 100, int(config.get('GENERAL', 'sndLimitLow')), int(config.get('GENERAL', 'sndLimitHigh')))
		os.system("amixer -q sset PCM -- %sdb" % volFactor)
		last_volume = volume

    ## Define DialPosition
    if dialPosition != last_dial and dialPosition <= int(config.get('GENERAL', 'dialWidth')):
        last_dial = dialPosition

        # Save station position into control file
        try:
            f = open('dial.tmp','w')
            try:
                f.write(str(int(dialPosition)))
            finally:
                f.close()
        except IOError:
            pass
   
    if not prevStation:
	    prevStation = 0
    while prevStation <= dialPosition:
    	prevStation = prevStation + betweenStations + int(config.get('GENERAL', 'stationWidth'))
    prevStation = prevStation - betweenStations - int(config.get('GENERAL', 'stationWidth'))
		
    nextStation = prevStation + betweenStations
    fadeLeft = prevStation + int(config.get('GENERAL', 'fadeWidth'))
    fadeRight = nextStation - int(config.get('GENERAL', 'fadeWidth'))
    station = nextStation + int(config.get('GENERAL', 'stationWidth'))

    print "prevStation: ", prevStation
    print "nextStation: ", nextStation
    print "fadeLeft:    ", fadeLeft
    print "fadeRight:   ", fadeRight
	
    # Between Stations
    playMode = None
    if dialPosition >= prevStation and dialPosition <= nextStation:
        ## Fade Left
        if dialPosition <= fadeLeft:
            print
            print "Actual Status: Fade Left"
            print
            volFactor = fadeLeft - int(config.get('GENERAL', 'fadeWidth')) + dialPosition
            os.system("amixer -q sset PCM "+ str(int(volFactor)) +"-%")

        ## Static Between Fades and Next Station
        elif dialPosition >= fadeLeft and dialPosition <= fadeRight:
            print
            print "Actual Status: Static"
            print

            if playMode != "static":
                playMode = "static"
                playStatus = 0
                staticLeft = fadeLeft + 5
                staticRight = fadeRight -5

            if dialPosition <= staticLeft:
                os.system("amixer -q sset PCM 2+%")
            elif dialPosition > staticRight:
                os.system("amixer -q sset PCM 2-%")
        
        ## Fade Right
        elif dialPosition >= fadeRight and dialPosition <= nextStation:
            print
            print "Actual Status: Fade Right"
            print

            if playMode != "radio":
                playMode = "radio"
                volFactor = fadeRight - int(config.get('GENERAL', 'fadeWidth')) + dialPosition
                os.system("amixer -q sset PCM "+ str(int(volFactor)) +"+%")
    ## Radio Range
    elif dialPosition >= nextStation and dialPosition <= nextStation + int(config.get('GENERAL', 'stationWidth')):
        playMode = "radio"


    playStatus = client.status()
    if playMode == "static":
        if playStatus["state"] != "play":
            client.clear()
            client.load("st")
            client.play(0)
            client.repeat(1)
    elif playMode == "radio":
        client.clear()
        client.load(selector)
        client.play(0)

    print "playMode: ", playMode
    print "tone:     ", tone
    print "volume:   ", volume
    print "dial:     ", dialPosition
    print "station:  "
    print "selector: ", selector

    time.sleep(1)

client.close()
client.disconnect()