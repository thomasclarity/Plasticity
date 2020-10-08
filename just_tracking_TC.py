"""
Author: tclarity

This script sends pulses to the Pointgrey camera via PulsePal to trigger frame capture. Start Bonsai then run this code
to prep the Bonsai workflow for live tracking.

The current script is specific for this PulsePal configuration:
Output Channel 1: Photometry
Output Channel 2: Laser
Output Channel 3: Camera GPIO

Script Runtime: 18 seconds of pulses + 2 second silent gap

Code adapted from justphotometry.py by RMikofsky

"""

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
StimDuration = 1*18
aquisitionFreq = 40


if aquisitionFreq == 40:
    PhotoUpTime = 0.017
    PhotoDownTime = 0.008

elif aquisitionFreq == 20:
    PhotoUpTime = 0.035
    PhotoDownTime = 0.015

#%%
# Pulse settings for output channel 3 (camera)

myPulsePal.programOutputChannelParam('isBiphasic', 3, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 3, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 3, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 3, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 3, PhotoUpTime)
myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, StimDuration)
myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, 0)  # No delay for prerecording

print("Prepping camera for live tracking")
myPulsePal.triggerOutputChannels(0, 0, 1, 0)
time.sleep(StimDuration + 2)
print("Starting Baseline Trial")


#myPulsePal.setDisplay("Ch 1 ON ", " Click for menu")

#msg = input('Type x and hit enter to stop pulses \n')
# if msg == 'x':
#     myPulsePal.abortPulseTrains()
#
# else:
#     time.sleep(StimDuration + 2)


