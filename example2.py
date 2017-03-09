import time

from naoqi import ALProxy
from naoqi import ALModule

IP = "192.168.1.100"
PORT = 9559

memory = ALProxy("ALMemory",IP,PORT)

asr = ALProxy("ALSpeechRecognition",IP,PORT)

asr.setLanguage("English")

wordList=["yes","no","hello NAO","goodbye NAO"]

# asr.setWordListAsVocabulary(wordList)

asr.subscribe("MySpeechRecognition")


def onWord(*args):
    print args


memory.subscribeToEvent("WordRecognized","WordRecognized", "onWord")



while True:
   time.sleep(1)
