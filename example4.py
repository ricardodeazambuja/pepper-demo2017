from naoqi import ALProxy
import time

rec = audio = None

global rec, audio

robot_IP = "192.168.1.100"

robot_PORT = 9559

audio = ALProxy("ALAudioDevice", robot_IP, robot_PORT)

#tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)

# ----------> Mute <----------
#if audio.isAudioOutMuted() == False:
#     audio.muteAudioOut(True)
#audio.muteAudioOut(False)




#tts.say("Humans")
rec = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)
channels = [1, 1, 1, 1] # Left, Right, Front, Rear
rec.startMicrophonesRecording("/home/nao/new.wav", "wav", 16000, channels)
time.sleep(5)
rec.stopMicrophonesRecording()
