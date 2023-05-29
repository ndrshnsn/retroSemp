#!/usr/bin/env python2
#
def cmdline(command):
	'''
	Execute command in shell and returns result
	'''
	from subprocess import PIPE, Popen

	process = Popen(
		args=command,
		stdout=PIPE,
		shell=True
	)
	return process.communicate()[0]

def loadPlaylists(playlist,file):
	'''
	Remove playlist, load Stations from text File into MPD Playlist
	'''
	cmdline("mpc clear")
	cmdline("mpc rm "+ playlist +"")

	with open(file) as f:
		lines = f.readlines()

	for line in lines:
		cmdline("mpc add "+ str(line) +"")

	cmdline("mpc save "+ playlist +"")

	return -1

def setEqual(value):
	'''
	Modify the current Equalizer (based on alsaequal) accordingly
	to the values passed from the equalizer table
	'''

	import string
	from array import array

	alsaControls = cmdline("./alsaControls.sh").splitlines()

	## Equalizer Table
	#
	equalTable = {}
	equalTable[0] = array('i',[90,85,75,75,75,65,65,60,50,60])
	equalTable[1] = array('i',[90,80,75,70,70,65,65,60,55,60])
	equalTable[2] = array('i',[85,80,70,70,65,60,65,70,60,65])
	equalTable[3] = array('i',[85,75,70,70,65,60,65,70,65,65])
	equalTable[4] = array('i',[80,75,65,60,60,60,60,80,70,70])
	equalTable[5] = array('i',[80,70,65,60,60,60,60,80,80,80])
	equalTable[6] = array('i',[70,70,65,60,60,60,60,80,80,80])
	equalTable[7] = array('i',[65,65,65,60,65,60,65,80,85,85])
	equalTable[8] = array('i',[65,60,60,65,65,60,65,85,85,85])
	equalTable[9] = array('i',[60,55,60,65,70,65,65,85,85,90])
	equalTable[10] = array('i',[60,50,60,65,75,65,65,85,90,90])

	
	for count in range(0,9):
		cmdline("amixer -D equal set '"+ str(alsaControls[count]) +"' "+ str(int(equalTable[value][count])) +"")

	return -1

def volMap(x, in_min, in_max, out_min, out_max):
	'''
	Returns the value that corresponds in a range from another
	'''
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min