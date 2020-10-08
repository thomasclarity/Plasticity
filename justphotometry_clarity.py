import time
import sys, os
import datetime
import zmq
import json

#sys.path.append('C:\\Users\\mikofskyrm\\PycharmProjects\\PulsePalProject\\PulsePal\\PulsePal-master\\Python\\PulsePal')
sys.path.append('C:\\Users\\GordonLabINS\\Documents\\PulsePal\\PulsePal-master\\Python')
from PulsePal import PulsePalObject  # Import PulsePalObject

myPulsePal = PulsePalObject()  # Create a new instance of a PulsePal object
myPulsePal.connect(serialPortName='COM10')  # Connect to PulsePal on port COM# (open port, handshake and receive firmware version)
print(myPulsePal.firmwareVersion)  # Print firmware version to the console

# Set these:
StimDuration = 1*30
aquisitionFreq = 20


if aquisitionFreq == 40:
    PhotoUpTime = 0.017
    PhotoDownTime = 0.008

elif aquisitionFreq == 20:
    PhotoUpTime = 0.035
    PhotoDownTime = 0.015

myPulsePal.programOutputChannelParam('isBiphasic', 1, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 1, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 1, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 1, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 1, PhotoUpTime)
myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, StimDuration)
myPulsePal.programOutputChannelParam('pulseTrainDelay', 1, 0)  # No delay for prerecording

#sendtimestamp(json.dumps(event_pre_start))
myPulsePal.triggerOutputChannels(1, 0, 0, 0)
#myPulsePal.setDisplay("Ch 1 ON ", " Click for menu")

msg = input('Type x and hit enter to stop pulses \n')
if msg == 'x':
    myPulsePal.abortPulseTrains()

else:
    time.sleep(StimDuration)

myPulsePal.setDisplay("Done", " Click for menu")

myPulsePal.disconnect()
print('done')
