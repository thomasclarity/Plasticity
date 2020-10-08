"""
Author: tclarity

Function: Sends pulses to the photometry system and camera while sending stimulation to the animal during a Plasticity
day of the Plasticity study.

    1. Sends 18 seconds of pulses to the camera to prep it for live tracking + 2 seconds of silence
    2. 10 minutes of baseline recording + 20 seconds of silence
    3. Plasticity day stimulation paradigm (~ 43 minutes)

The current script is specific for this PulsePal configuration:
Output Channel 1: Photometry
Output Channel 2: Laser
Output Channel 3: Camera GPIO

Code adapted from justphotometry.py and Photometry_Plasticity40Hz by RMikofsky

"""

import time
import sys, os
import datetime
import zmq
import json

# ==================================  Change These For Your Computer  ===========================================

sys.path.append('C:\\Users\\GordonLabINS\\Documents\\PulsePal\\PulsePal-master\\Python')        # Path to PulsePal code
from PulsePal import PulsePalObject  # Import PulsePalObject

myPulsePal = PulsePalObject()  # Create a new instance of a PulsePal object
myPulsePal.connect(serialPortName='COM10')  # Connect to PulsePal on port COM# (open port, handshake and receive firmware version)
print(myPulsePal.firmwareVersion)  # Print firmware version to the console

# ******************* CHANGE THESE TO CALIBRATE LASER ******************************************************
laserpowerboosterMultiplier = 0.00 # range 0.025-0.05
laserpowerbooserAdditive = 0.00 # range 0.1-0.4
#***********************************************************************************************************

# ==================================  Setting up comments to Open Ephys   ===========================================
# WARNING MUST SAVE OPEN EPHYS FILES AS "Binary" TYPE

def sendtimestamp(timestamp):
    ip = '127.0.0.1'
    port = 5041     # change this number for each computer
    timeout = 1.

    url = "tcp://%s:%d" % (ip, port)

    with zmq.Context() as context:
        with context.socket(zmq.REQ) as socket:
            socket.RCVTIMEO = int(timeout * 1000)  # timeout in milliseconds
            socket.connect(url)

            socket.send_string(timestamp)
sendtimestamp(timestamp='testing')
myPulsePal.setDisplay("PYTHON hello", " Click for menu")


# ==================================  Input Experimental Data   ===========================================

print('Please enter all of the experimental metadata in all lowercase except protocol name')

#This first set of messages will make up metadata for this experiment that is already included with every comment. So it will be automatically included in analysis.
msg_mouse = input('Type mouse ID (ex. "m123") and hit enter. \n')
msg_protocol = input('Type protocol (ex. "IO" or "Plasticity" - for this code it should be "Plasticity") and hit enter. \n')

#This portion is a fail-safe test to make sure the correct input is given. It can be adapted to make sure any input is without typos and correct/consistent (one of a few desired options)
protocolinputtest = 'false'
while protocolinputtest == 'false':
    if msg_protocol == 'Plasticity':
        protocolinputtest = 'true'
    elif msg_protocol == 'IO':
        print("This is not the IO protocol. Quit this protocol and open PulseFreqv2")
    else:
        print ('That is not a valid option, try again')
        msg_protocol = input('Type protocol (ex. "IO" or "Plasticity" - for this code it should be "Plasticity") and hit enter. \n')


msg_week = input('Type test week (ex. "w1") and hit enter.  \n')
msg_dayinweek = input('Type test day of week (ex. "d1" is first day of that week) and hit enter.  \n')
msg_sexmouse = input('Type the sex of the mouse ("m", "f") and hit enter. \n')
msg_mutantmouse = input('Type mouse mutant status (ex. "wt", "df16", "setd1a") and hit enter. \n')
msg_laserpower = input('Enter laser power to be used (in mW) or "variable" and hit Enter. \n')


msg_plasticitystim = input('Type the plasticity condition, "HFS" or "nostim" if this is a plasticity no stim control and hit enter. \n')

#This portion is a fail-safe test to make sure the correct input is given for the protocol to run the correct plasticity paradigm. It can be adapted to make sure any input is without typos and correct/consistent (one of a few desired options)
plasticityinputtest = 'false'
while plasticityinputtest == 'false':
    if msg_plasticitystim == 'HFS':
        PlasticityType = 'HFS'
        plasticityinputtest = 'true'
    elif msg_plasticitystim == 'nostim':
        PlasticityType = 'nostim'
        plasticityinputtest = 'true'
    else:
        print ('That is not a valid option for plasticity, try again')
        msg_plasticitystim = input(
            'Type "HFS" if plasticity stim should be on and "nostim" if this is a no plasticity stim control and hit enter. \n')

#This second set of messages will make up metadata for this experiment that will only be included in a header comment. It can be added to analysis later but will not be included right away to keep the comments from being too large/long.
print('Following information will be about virus injections, etc. gcamp is always primary if it is present. \n')
msg_twoindicators = input('Are there two indicators (gcamp, geco) or only one? Type "one" or "two" and hit enter. \n')
msg_twoopsins = input('Are there two opsins (chrimson, channel) or only one? Type "one" or "two" and hit enter. \n')

msg_virusweeks = input('Type how many weeks since virus injection at experiment start (ex. "9") and hit enter. \n')

if msg_twoindicators == 'one':
    msg_reportercelltype1 = input('Type the primary reporter celltype ("sst", "camk", "pv", "vip") and hit enter.  \n')
    msg_reporterindicator1 = input('Type the primary reporter indicator ("gcamp", "geco", "tdtom", "egfp") and hit enter.  \n')
    msg_reportertiter1 = input('Type the primary reporter viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')
    msg_reportercelltype2 = 'NA'
    msg_reporterindicator2 = 'NA'
    msg_reportertiter2 = 'NA'
    msg_virusratio = 'NA'

elif msg_twoindicators == 'two':
    msg_virusratio = input(
        'If there are two viruses in PFC, type the ratio between the primary (default gcamp) and secondary (ex. gcamp to tomato in ratio 4 to 1 input as "4to1"). Then press enter. \n')
    msg_reportercelltype1 = input('Type the primary reporter celltype ("sst", "camk", "pv", "vip") and hit enter.  \n')
    msg_reporterindicator1 = input('Type the primary reporter indicator ("gcamp", "geco", "tdtom", "egfp") and hit enter.  \n')
    msg_reportertiter1 = input('Type the primary reporter viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')
    msg_reportercelltype2 = input('Type the secondary reporter cell type ("sst", "camk", "pv", "vip") or NA if none is present and hit enter.  \n')
    msg_reporterindicator2 = input('Type the secondary reporter indicator ("gcamp", "geco", "tdtom", "egfp") or NA if none is present and hit enter.  \n')
    msg_reportertiter2 = input('Type the secondary reporter viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')


if msg_twoopsins == 'one':
    msg_opsincelltype1 = input('Type the primary opsin celltype ("hpc", "sst", "camk", "pv", "vip") and hit enter.  \n')
    msg_opsinconstruct1 = input('Type the primary opsin construct ("chrimson", "channel") and hit enter.  \n')
    msg_opsintiter1 = input('Type the primary opsin viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')
    msg_opsincelltype2 = 'NA'
    msg_opsinconstruct2 = 'NA'
    msg_opsintiter2 = 'NA'

elif msg_twoopsins == 'two':
    msg_opsincelltype1 = input('Type the primary opsin celltype ("hpc", "sst", "camk", "pv", "vip") and hit enter.  \n')
    msg_opsinconstruct1 = input('Type the primary opsin construct ("chrimson", "channel") and hit enter.  \n')
    msg_opsintiter1 = input('Type the primary opsin viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')
    msg_opsincelltype2 = input('Type the secondary opsin celltype ("hpc", "sst", "camk", "pv", "vip") and hit enter.  \n')
    msg_opsinconstruct2 = input('Type the secondary opsin construct ("chrimson", "channel") and hit enter.  \n')
    msg_opsintiter2 = input('Type the secondary opsin viral titer (ex. type "2_3x10_13" for 2.3 x 10^13) and hit enter.  \n')

msg_enter = input('Finally, type any key and hit enter to start session. \n')


# ==========================================  Setup Baseline Comments  ==========================================================

fileid = msg_mouse + '_' + msg_protocol + '_' + msg_week + msg_dayinweek
sendtimestamp(timestamp='StartAcquisition')
sendtimestamp('StartRecord PrependText=' + fileid)

sendtimestamp(json.dumps('Photometry recording Plasticity experiment'))

#This is the header comment that includes all the metadata, including the header-only metadata.
headertimestamp = {'event_type': 'header', 'startdatetime': str(datetime.datetime.now()), 'mouse': msg_mouse, 'protocol': msg_protocol,
                   'week': msg_week, 'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                   'sexmouse':msg_sexmouse, 'mutantmouse': msg_mutantmouse, 'laserpower': str(msg_laserpower),
                   'virusweeks': msg_virusweeks, 'virusratio':msg_virusratio, 'reportercelltype1' : msg_reportercelltype1,
                   'reporterindicator1': msg_reporterindicator1, 'reportertiter1': msg_reportertiter1,
                   'reportercelltype2': msg_reportercelltype2, 'reporterindicator2': msg_reporterindicator2,
                   'reportertiter2': msg_reportertiter2, 'msg_opsincelltype1': msg_opsincelltype1,
                   'opsinconstruct1': msg_opsinconstruct1, 'opsintiter1':msg_opsintiter1,
                   'opsincelltype2': msg_opsincelltype2, 'opsinconstruct2': msg_opsinconstruct2,
                   'opsintiter2': msg_opsintiter2}
sendtimestamp(json.dumps(headertimestamp))
print(headertimestamp)

# These are the comments sent at the start and end of Baseline
base_start = {'stim_event': 'baseline', 's_or_e_of_event': 'start', 'event_type': 'Plasticity',
                   'pulse_width': 'NA', 'pulse_frequency': 'NA', 'pulse_n': 'NA',
                   'pulse_laserpower': 'NA',
                   'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                   'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                   'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                   'laserpower': 'NA',
                   'trial_inday': 'NA', 'trial_inphase': 'NA', 'round': 'NA',
                   'trial_inround': 'NA', 'plasticity_type': PlasticityType, 'stim_type': 'NA',
                   'test_pulse_type': 'NA'}

base_end = {'stim_event': 'baseline', 's_or_e_of_event': 'end', 'event_type': 'Plasticity',
                   'pulse_width': 'NA', 'pulse_frequency': 'NA', 'pulse_n': 'NA',
                   'pulse_laserpower': 'NA',
                   'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                   'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                   'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                   'laserpower': 'NA',
                   'trial_inday': 'NA', 'trial_inphase': 'NA', 'round': 'NA',
                   'trial_inround': 'NA', 'plasticity_type': PlasticityType, 'stim_type': 'NA',
                   'test_pulse_type': 'NA'}

sendtimestamp("testing")

# ============================  PulsePal Settings for 20 Second Camera Prep  ===========================================
PrepCamDuration = 1*18
aquisitionFreq = 40


if aquisitionFreq == 40:
    PhotoUpTime = 0.017
    PhotoDownTime = 0.008

elif aquisitionFreq == 20:
    PhotoUpTime = 0.035
    PhotoDownTime = 0.015

#%%
# =========================== Set-Up Output Channel 3, goes to camera =============================================

myPulsePal.programOutputChannelParam('isBiphasic', 3, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 3, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 3, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 3, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 3, PhotoUpTime)
myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, PrepCamDuration)
myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, 0)  # No delay for prerecording

# =========================== Send 18 seconds of pulses to prep camera  =======================================

print("Prepping camera for live tracking")
myPulsePal.triggerOutputChannels(0, 0, 1, 0)
time.sleep(PrepCamDuration + 2)    # 18 secs of pulses + 2 secs of silence


# ============================  PulsePal Settings for 10 min Baseline Trial  ===========================================

BaselineDuration = 1*600
aquisitionFreq = 40


if aquisitionFreq == 40:
    PhotoUpTime = 0.017
    PhotoDownTime = 0.008

elif aquisitionFreq == 20:
    PhotoUpTime = 0.035
    PhotoDownTime = 0.015

# ==================== Set-Up Output Channel 1, goes to photometry =======================================

myPulsePal.programOutputChannelParam('isBiphasic', 1, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 1, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 3, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 1, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 1, PhotoUpTime)
myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, BaselineDuration)
myPulsePal.programOutputChannelParam('pulseTrainDelay', 1, 0)  # No delay for prerecording

# =========================== Set-Up Output Channel 3, goes to camera =============================================

myPulsePal.programOutputChannelParam('isBiphasic', 3, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 3, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 3, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 3, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 3, PhotoUpTime)
myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, BaselineDuration)
myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, 0)  # No delay for prerecording

# =========================== Send pulses to photometry and camera for Baseline Trial  ==============================

print("Starting Baseline Trial")
sendtimestamp(json.dumps('Photometry recording Plasticity Baseline'))
sendtimestamp(json.dumps(base_start))
myPulsePal.triggerOutputChannels(1, 0, 1, 0)
print(base_start)
time.sleep(BaselineDuration)    # 10 mins baseline
sendtimestamp(json.dumps(base_end))
print(base_end)
time.sleep(20)      # 20 secs of silence


# ======================================  Plasticity Phase Settings  =================================================
# ========================================= Plasticity Parameters ====================================================

interTrialinterval = 2 #DO NOT CHANGE THIS

rounds_plasticity = 80 # Default 60, CHANGE THIS BACK
nPulses_plasticity = [40] # Default to 40

if PlasticityType == 'HFS':
    freq_plasticity = [40]

elif PlasticityType == 'nostim':
    freq_plasticity = [40]

PreRecordingDuration_plasticity = 10 #Default to 10
PostRecordingDuration_plasticity = 20 #Default to 20

pulseWidth_plasticity = 0.005
laserpower_plasticity = 5

# ========================================== Parameters - Defaults ===================================================
StimFrequency = 40  # Default to 40
PulseWidth = 0.005  # Default to 0.005
LaserPower = 5  # in mW
nPulses = 1
upVoltage = 3 # Will be overwritten by calculation later
downVoltage = 1


# +++ DO NOT CHANGE THIS:
PhotoStimDelay = 0.005  # Default to 0.005 so that recording doesn't overlap with pulses
PhotoUpTime = 0.017
PhotoDownTime = 0.008


testingTime = (rounds_plasticity*32)/60     #(((rounds_TP * len(nPulses_TP) * 2)*62) +


# ================================== Set-Up Output Channel 1 goes to photometry ======================================
# Program output channel 1 to use monophasic pulses (isBiphasic = 0)

myPulsePal.programOutputChannelParam('isBiphasic', 1, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 1, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 1, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 1, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 1, PhotoUpTime)

# ================================== Set-Up Output Channel 3 goes to camera ==========================================

myPulsePal.programOutputChannelParam('isBiphasic', 3, 0)
myPulsePal.programOutputChannelParam('phase1Voltage', 3, 5)
myPulsePal.programOutputChannelParam('interPulseInterval', 3, PhotoDownTime)
myPulsePal.programOutputChannelParam('restingVoltage', 3, 0)
myPulsePal.programOutputChannelParam('phase1Duration', 3, PhotoUpTime)

# ================================== Initiate Plasticity Stimulation Paradigm =========================================

sendtimestamp(json.dumps('Photometry recording plasticity stimulation'))

trial_inday = 0
trial_inphase = 0
thisround = 0
trial_inround = 0
StimType = 'NA'
TestPulseType = 'NA'

sendtimestamp("testing")

# ========================================== Plasticity Stimulation ====================================================
trial_inphase = 0

numRounds = rounds_plasticity
numTrials = rounds_plasticity * len(nPulses_plasticity)
TestPulseType = 'NA' # before, after, or NA
StimType = 'plasticity' # This refers to this specific phase (TP, plasticity)

testingTime = ((numTrials * (PreRecordingDuration_plasticity + PostRecordingDuration_plasticity + interTrialinterval)) / 60)

print('Starting Plasticity. Current time is ' + str(datetime.datetime.now()) + '. This phase will be done in about ' + str(testingTime) + ' minutes.')

for thisround in range(1, rounds_plasticity+1):
    trial_inround = 0
    print('\n Starting plasticity round ' + str(thisround) + ' of ' + str(numRounds))

    PulseWidth = pulseWidth_plasticity
    LaserPower = laserpower_plasticity
    upVoltage = ((LaserPower + 21.813) / 11.238) * (
            1 + (laserpowerboosterMultiplier * LaserPower)) + laserpowerbooserAdditive

    PreRecordingDuration = PreRecordingDuration_plasticity
    PostRecordingDuration = PostRecordingDuration_plasticity

    for StimFrequency in freq_plasticity:

        for nPulses in nPulses_plasticity:
            StimDuration = (1.0000 / StimFrequency) * nPulses
            ipiDuration = (1.0000 / StimFrequency) - PulseWidth

            # These are the comments sent within each trial
            event_pre_start = {'stim_event': 'off_pre', 's_or_e_of_event': 'start', 'event_type': 'stim',
                               'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                               'pulse_laserpower': LaserPower,
                               'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                               'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                               'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                               'laserpower': str(msg_laserpower),
                               'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                               'trial_inround': trial_inround, 'plasticity_type': PlasticityType, 'stim_type': StimType,
                               'test_pulse_type': TestPulseType}
            event_pre_end = {'stim_event': 'off_pre', 's_or_e_of_event': 'end', 'event_type': 'stim',
                             'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                             'pulse_laserpower': LaserPower,
                             'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week, 'dayinweek': msg_dayinweek,
                             'fileid': fileid, 'plasticitystim': msg_plasticitystim, 'sexmouse': msg_sexmouse,
                             'mutant_mouse': msg_mutantmouse, 'laserpower': str(msg_laserpower),
                             'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                             'trial_inround': trial_inround, 'plasticity_type': PlasticityType, 'stim_type': StimType,
                             'test_pulse_type': TestPulseType}

            event_stim_start = {'stim_event': 'on_stim', 's_or_e_of_event': 'start', 'event_type': 'stim',
                                'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                                'pulse_laserpower': LaserPower,
                                'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                                'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                                'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                                'laserpower': str(msg_laserpower),
                                'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                                'trial_inround': trial_inround, 'plasticity_type': PlasticityType,
                                'stim_type': StimType, 'test_pulse_type': TestPulseType}
            event_stim_end = {'stim_event': 'on_stim', 's_or_e_of_event': 'end', 'event_type': 'stim',
                              'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                              'pulse_laserpower': LaserPower,
                              'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                              'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                              'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                              'laserpower': str(msg_laserpower),
                              'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                              'trial_inround': trial_inround, 'plasticity_type': PlasticityType, 'stim_type': StimType,
                              'test_pulse_type': TestPulseType}

            event_post_start = {'stim_event': 'off_post', 's_or_e_of_event': 'start', 'event_type': 'stim',
                                'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                                'pulse_laserpower': LaserPower,
                                'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                                'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                                'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                                'laserpower': str(msg_laserpower),
                                'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                                'trial_inround': trial_inround, 'plasticity_type': PlasticityType,
                                'stim_type': StimType, 'test_pulse_type': TestPulseType}
            event_post_end = {'stim_event': 'off_post', 's_or_e_of_event': 'end', 'event_type': 'stim',
                              'pulse_width': PulseWidth, 'pulse_frequency': StimFrequency, 'pulse_n': nPulses,
                              'pulse_laserpower': LaserPower,
                              'mouse': msg_mouse, 'protocol': msg_protocol, 'week': msg_week,
                              'dayinweek': msg_dayinweek, 'fileid': fileid, 'plasticitystim': msg_plasticitystim,
                              'sexmouse': msg_sexmouse, 'mutant_mouse': msg_mutantmouse,
                              'laserpower': str(msg_laserpower),
                              'trial_inday': trial_inday, 'trial_inphase': trial_inphase, 'round': thisround,
                              'trial_inround': trial_inround, 'plasticity_type': PlasticityType, 'stim_type': StimType,
                              'test_pulse_type': TestPulseType}

            print("\n Starting Trial " + str(trial_inphase) + ' round trial ' + str(
                trial_inround) + ' . PulseWidth is ' + str(
                PulseWidth) + '. StimFrequency is ' + str(StimFrequency) + '. nPulses is ' + str(
                nPulses) + '. Laser Power is ' + str(LaserPower))

            # testcomment = json.dumps({'test1':1, 'test2': 2})

            # ==================== Modify Output Channel 1 to photometry ======================================================
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, PreRecordingDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 1, 0)  # No delay for prerecording

            # ==================== Modify Output Channel 3 to camera ======================================================
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, PreRecordingDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, 0)  # No delay for prerecording

            myPulsePal.syncAllParams()
            # ==================== Set-Up Output Channel 2 goes to red laser ======================================================
            # Program output channel 2 to use monophasic pulses (isBiphasic = 0)
            myPulsePal.programOutputChannelParam('isBiphasic', 2, 0)
            myPulsePal.programOutputChannelParam('phase1Voltage', 2, upVoltage)
            myPulsePal.programOutputChannelParam('interPulseInterval', 2, ipiDuration)
            myPulsePal.programOutputChannelParam('restingVoltage', 2, downVoltage)
            myPulsePal.programOutputChannelParam('phase1Duration', 2, PulseWidth)
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 2, StimDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 2, 0)  # no delay
            myPulsePal.setContinuousLoop(2, 0)  # not looping forever

            myPulsePal.syncAllParams()

            # ============================ Pre-Stim Recording + Camera ================================================
            #sendtimestamp("testing")
            # print(testcomment)
            sendtimestamp(json.dumps(event_pre_start))
            myPulsePal.triggerOutputChannels(1, 0, 1, 0)  # Soft-trigger channels 1
            print(event_pre_start)
            #print('starting pre-recording, will go for ' + str(PreRecordingDuration) + ' seconds before stopping')
            # myPulsePal.setDisplay("Ch 1 ON PreStim", " Click for menu")
            time.sleep(PreRecordingDuration)
            #print('done pre-recording')
            sendtimestamp(json.dumps(event_pre_end))
            # myPulsePal.setDisplay("Ch 1 OFF PreStim", " Click for menu")
            print(event_pre_end)

            # =========================== Stim + Recording + Camera =======================================================
            # Change channel 1 properties first:
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, StimDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 1,
                                                 PhotoStimDelay)  # Delay for first stim pulse (pulse width + 5ms)

            # Change channel 3 properties first:
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, StimDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, PhotoStimDelay)  # Delay for first camera pulse (pulse width + 5ms)

            sendtimestamp(json.dumps(event_stim_start))

            if PlasticityType == 'HFS':
                myPulsePal.triggerOutputChannels(1, 1, 1, 0)  # Soft-trigger channels 1, 2, and 3

            elif PlasticityType == 'nostim':
                myPulsePal.triggerOutputChannels(1, 0, 1, 0)  # Soft-trigger channels 1 and 3

            print(event_stim_start)
            # print('Stim - Both channels on')
            # myPulsePal.setDisplay("Ch 1, 2 ON Stim", " Click for menu")
            time.sleep(StimDuration)
            # print('Stim - Both channels off')
            sendtimestamp(json.dumps(event_stim_end))
            # myPulsePal.setDisplay("Ch 1, 2 OFF Stim", " Click for menu")
            print(event_stim_end)

            # ============================ Post-Stim Recording + Camera ================================================
            # Change channel 1 properties first:
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, PostRecordingDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 1, 0)  # No delay for post-stim recording

            # Change channel 3 properties first:
            myPulsePal.programOutputChannelParam('pulseTrainDuration', 3, PostRecordingDuration)
            myPulsePal.programOutputChannelParam('pulseTrainDelay', 3, 0)  # No delay for post-stim recording

            sendtimestamp(json.dumps(event_post_start))
            myPulsePal.triggerOutputChannels(1, 0, 1, 0)  # Soft-trigger channels 1

            print(event_post_start)
            #print('starting post-recording pulse, will go for ' + str(PostRecordingDuration) + ' seconds before stopping')
            # myPulsePal.setDisplay("Ch 1 ON PostStim", " Click for menu")
            time.sleep(PostRecordingDuration)
            # print('Ch1 has ended pulses')
            sendtimestamp(json.dumps(event_post_end))
            # myPulsePal.setDisplay("Ch 1 OFF PostStim", " Click for menu")
            print(event_post_end)

            endMessage = 'Done ' + str(trial_inphase+1) + ' of ' + str(numTrials)
            myPulsePal.setDisplay(str(endMessage), " Click for menu")

            print(endMessage)
            trial_inday += 1
            trial_inphase += 1
            trial_inround += 1
            time.sleep(interTrialinterval)

time.sleep(interTrialinterval)

print('Done with everything!')
sendtimestamp('StopRecord')
